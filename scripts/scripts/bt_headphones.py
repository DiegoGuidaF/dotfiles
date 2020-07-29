#!/usr/bin/env python3
import signal
import dbus
from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop
from bluepy import btle
import argparse
import logging
import json
import sys
import threading
from functools import partial
import os
import subprocess
import time

SCRIPT_NAME = "bt-headphones"
logger = logging.getLogger(SCRIPT_NAME)

ADAPTER_NAME = "hci0"
ADAPTER_FULL_NAME = "/org/bluez/" + ADAPTER_NAME
BUS_NAME = 'org.bluez'
ADAPTER_INTERFACE = BUS_NAME + '.Adapter1'
DEVICE_INTERFACE = BUS_NAME + '.Device1'

BATTERY_LEVEL_HANDLER=0x002d

class BluetoothHandler(btle.DefaultDelegate):

    def __init__(self, bus, address):
        btle.DefaultDelegate.__init__(self)
        self.address = address
        self.bus = bus
        self.address_dbus = address.replace(":","_")
        self.battery = -1
        # Interface for interacting with the adapter
        self.adapter_object = bus.get_object(BUS_NAME,
                       '/org/bluez/hci0')
        self.adapter_props_iface = dbus.Interface(self.adapter_object,
            dbus_interface='org.freedesktop.DBus.Properties')

        self.device_object = bus.get_object(BUS_NAME,
                       f'/org/bluez/hci0/dev_{self.address_dbus}')
        # Interface for interacting with the device (connect, disconnect...)
        self.device_iface = dbus.Interface(self.device_object,
            dbus_interface=DEVICE_INTERFACE)
        
        # Interface for querying properties
        self.device_props_iface = dbus.Interface(self.device_object,
            dbus_interface='org.freedesktop.DBus.Properties')

        try:
            self.is_connected = self.get_device_property("Connected")
            self.is_adapter_blocked = False
        except dbus.exceptions.DBusException:
            logger.debug("Adapter is blocked")
            self.is_adapter_blocked = True
            self.is_connected = False

    def get_adapter_property(self, prop_name):
        prop_value = self.adapter_props_iface.Get(ADAPTER_INTERFACE, prop_name)
        logger.debug(f"Adapter property {prop_name} value is: {prop_value}")
        return prop_value

    def set_adapter_property(self, prop_name, value):
        prop_value = self.adapter_props_iface.Set(ADAPTER_INTERFACE, prop_name, value)
        logger.debug(f"Adapter property {prop_name} set to {value}")
        return prop_value

    def toggle_connection(self):
        if not self.is_connected:
            self.connect()
        else:
            self.disconnect()

    def start_listen_loop(self):
        self.subscribe_to_dbus_signals()
        self.print_status()
        # Setup read battery updates loop
        if self.is_connected:
            self.start_read_battery_thread()

    def start_read_battery_thread(self):
        t = threading.Thread(target=self.battery_notifications_loop)
        t.daemon = True
        t.start()

    def properties_changed_handler(self, interface, new, old, **kw):
        response = {}
        response['event'] = "PropertiesChanged"
        response['interfaces'] = interface
        response["properties"] = new
        logger.debug(f"Received new event: {json.dumps(response)}")
        has_changes = False

        if interface == DEVICE_INTERFACE and "Connected" in response["properties"]:
            has_changes = self.on_connection_changed(bool(response["properties"]["Connected"]))

        if has_changes:
            self.print_status()

    def interfaces_added_handler(self, interface, props, **kw):
        response = {}
        response['event'] = "InterfaceAdded"
        response['interfaces'] = interface
        response["properties"] = props

        if interface == ADAPTER_FULL_NAME:
            logger.info(f"Adapter {ADAPTER_NAME} unblocked")
            self.is_adapter_blocked = False
            self.print_status()

    def interfaces_removed_handler(self, interface, props, **kw):
        response = {}
        response['event'] = "InterfaceRemoved"
        response['interfaces'] = interface
        response["properties"] = props

        if interface == ADAPTER_FULL_NAME:
            logger.info(f"Adapter {ADAPTER_NAME} blocked")
            self.is_adapter_blocked = True
            self.print_status()

    def on_connection_changed(self, is_connected):
        has_changes = False
        # Only process is status is different than previous
        if self.is_connected != is_connected:
            has_changes = True
            self.is_connected = is_connected
            logger.info(f"Connection status changed to {self.is_connected}")
            # If connection is on, start listening for battery updates
            if is_connected:
                self.start_read_battery_thread()

        return has_changes

    def get_device_property(self, prop_name):
        prop_value = self.device_props_iface.Get(DEVICE_INTERFACE,prop_name)
        logger.debug(f"Device property {prop_name} value is: {prop_value}")
        return prop_value

    def subscribe_to_dbus_signals(self):
        logger.debug("Subscribing to property changes")
        self.bus.add_signal_receiver(self.properties_changed_handler,
            bus_name=BUS_NAME,
            path_keyword='path',
            signal_name="PropertiesChanged")

        logger.debug("Subscribing to interfaces added")
        self.bus.add_signal_receiver(self.interfaces_added_handler,
            bus_name=BUS_NAME,
            path_keyword='path',
            signal_name="InterfacesAdded")

        logger.debug("Subscribing to interfaces removed")
        self.bus.add_signal_receiver(self.interfaces_removed_handler,
            bus_name=BUS_NAME,
            path_keyword='path',
            signal_name="InterfacesRemoved")

    def power_off(self,block_on_power_off=False):
        is_powered = self.get_power_status()

        if not self.is_adapter_blocked:
            # First turn adapter off
            if is_powered:
                logger.info("Turning adapter off")
                self.set_adapter_property("Powered",dbus.Boolean(False))
            # Block it if requested, parameter exists since this asks for password via a Dialog,
            # so sometimes it might be skipped.
            if block_on_power_off:
                logger.debug("Blocking adapter")
                ret = subprocess.check_call(["pkexec","rfkill","block","bluetooth"])
                if ret != 0:
                    logger.error("Failed unblocking adapter")
                    return
                # Wait for the adapter to turn on
                while not self.is_adapter_blocked:
                    time.sleep(0.5)
                    self.get_power_status()

    def get_power_status(self):
        try:
            is_powered = self.get_adapter_property("Powered")
            self.is_adapter_blocked = False
        except dbus.exceptions.DBusException:
            logger.debug("Adapter is blocked")
            is_powered = False
            self.is_adapter_blocked = True

        return is_powered

    def power_on(self):
        """ Power on/off the bluetooth.
            Also block/unblock via rfkill since currently bluetooth
            is only used for the headphones.
        """
        # Check current adapter status
        is_powered = self.get_power_status()

        while not is_powered:
            logger.debug("Loop powering up adapter...")
            # Note thay, for an unknown reason, when unblocking the bluetooth adapter
            # a second adapter appears in rfkill with blocked state but the dbus adapter
            # is detected and works expect for the powering part, which can never be set to true
            # without raising any exception and therefore the is_powered is never true
            # unless the rfkill is unblocked again.
            # Rfkill output with second adapter:
            # 0 bluetooth tpacpi_bluetooth_sw unblocked unblocked
            # 1 wlan      phy0                unblocked unblocked
            # 4 bluetooth hci0                  blocked unblocked
            #
            rfkill_adapters = json.loads(subprocess.check_output(["rfkill","-J"]))
            rfkill_status = [adapter["soft"] for adapter in rfkill_adapters[''] if adapter["type"] == "bluetooth"]
            logger.debug(f"Rfkill: {rfkill_status}")
            
            if "blocked" in rfkill_status:
                logger.debug("Unblocking adapter")
                ret = subprocess.check_call(["pkexec","rfkill", "unblock", "bluetooth"])
                if ret != 0:
                    logger.error("Failed unblocking adapter")
                    raise Exception
                # Wait for the device to turn on by checking the Dbus interface.
                while self.is_adapter_blocked:
                    is_powered = self.get_power_status()
                    time.sleep(0.5)

            try:
                logger.info("Turning adapter on")
                self.set_adapter_property("Powered",dbus.Boolean(True))
            except dbus.exceptions.DBusException:
                logger.error("Couldn't set adapter power via Dbus")
                pass
            time.sleep(0.5)

            is_powered = self.get_adapter_property("Powered")

        else:
            logger.info("Bluetooth already in the desired state")
        
    def connect(self):
        # Ensure adapter is powered on
        self.power_on()

        if not self.is_connected:
            logger.info(f"Connecting to device {self.address}")
            self.device_iface.Connect()
        else:
            logger.info(f"Already connected to device {self.address}")

    def disconnect(self):
        if self.is_connected:
            logger.info(f"Disconnecting from device {self.address}")
            self.device_iface.Disconnect()
        else:
            logger.info("No device to disconnect")
        # Power off the adapter
        self.power_off()

    def connect_btle(self):
        # Ensure we are disconnected
        try:
            self.btle_dev.disconnect()
        except Exception:
            pass

        # Stablish connection and callbacks to self
        try:
            self.btle_dev.connect(self.address)
            self.btle_dev.setDelegate(self)
        except Exception:
            logger.error("Failed connecting to BTLE, retrying...")
            pass

    def battery_notifications_loop(self):
        logger.info("--Starting battery notification handler...")
        self.btle_dev = btle.Peripheral()
        self.connect_btle()

        logger.info("Listening for battery notifications")
        while self.is_connected:
            try:
                self.btle_dev.waitForNotifications(5)
            except Exception as e:
                logger.error(f"Error while waiting for bat. notification {e}")
                time.sleep(5)
                logger.info("Reconnecting BTLE...")
                self.btle_dev.disconnect()
                self.connect_btle()

        logger.info("--Stopped listening for battery notifications")
        self.btle_dev.disconnect()

    def print_status(self):
        logger.info('Writing changes to console')
        output = {}
        if self.is_connected:
            icon = ""
            status = "bat-"
            output["tooltip"] = f"Connected - Battery:  {self.battery}%"
            #Only send percentage is connected and available
            if self.battery != -1:
                output["percentage"] = self.battery

            if self.battery >= 60:
                status += "good"
            elif self.battery >= 60:
                status += "good"
            elif self.battery >= 30:
                status += "warning"
            elif self.battery >= 0:
                status += "critical"
            else:
                status += "unknown"
        elif self.is_adapter_blocked:
            icon = ""
            status = "blocked"
            output["tooltip"] = f"Blocked"
        elif not self.is_connected:
            icon = ""
            status = "disconnected"
            output["tooltip"] = f"Disconnected"
        else:
            icon = "?"
            status = "unknown"
            output["tooltip"] = f"Unknown state\nConnected {self.is_connected}\nBlocked {self.is_adapter_blocked}"

        
        output["text"] = icon
        output["class"] = status
                
        logger.debug(json.dumps(output))
    
        sys.stdout.write(json.dumps(output) + '\n')
        sys.stdout.flush()

    def handleNotification(self, cHandle, data):
        logger.debug("Received notification from BLE")
        if cHandle == BATTERY_LEVEL_HANDLER:
            new_bat = ord(data)
            if self.battery != new_bat:
                logger.info(f"Received battery update, new: {new_bat}% - old: {self.battery}")
                self.battery = new_bat
                self.print_status()
        else:
            logger.debug("Received unknown notification from BLE")
            logger.debug(f"Handle: {cHandle}")
            logger.debug(f"Data: {data}")

    def stop(self):
        try:
            self.btle_dev.disconnect()
            # Before finishing, set battery to an unknown state
            # so that this is also evident on output parsing scripts
            self.battery = -1
            self.print_status()
        except Exception:
            pass

def parse_arguments():
    parser = argparse.ArgumentParser()

    # Increase verbosity with every occurance of -v
    parser.add_argument('-v', '--verbose', action='count', default=0)
    # Define for which player we're listening
    parser.add_argument('address', metavar='addr', type=str,
                    help='Bluetooth address of the headphones.')

    # Mutually exclusive group, one of this options must be specified AT MOST.
    mxg = parser.add_mutually_exclusive_group(required=True)
    mxg.add_argument('--listen', action='store_true', help="Listen for connectivity and battery changes")
    mxg.add_argument('--toggle', action='store_true', help="Toggle bluetooth connection")
    mxg.add_argument('--power-off', action='store_true', help="Disconnect and block the bluetooth")

    return parser.parse_args()

def ensure_one_instance(script_name):
    """ Ensure there's only one instance of this script running.
        If another instance already running, kill it.
    """
    #script_name = f'{__file__}'.rstrip('.py').lstrip('./')
    pid_file = f'{os.getenv("XDG_RUNTIME_DIR")}/{script_name}.pid'

    #This is to check if there is already a lock file existing#
    if os.access(pid_file, os.F_OK):
        logger.info("PID file already exists")
        #if the lockfile is already there then check the PID number 
        #in the lock file
        with open(pid_file, "r") as pf:
            pf.seek(0)
            old_pid_num = pf.readline()
            # Now we check the PID from lock file matches to the current
            # process PID
            if os.path.exists(f"/proc/{old_pid_num}"):
                logger.debug("You already have an instance of the program running")
                logger.debug("It is running as process %s" % old_pid_num)
                logger.info("Killing it..")
                # Kill process!
                os.kill(int(old_pid_num), signal.SIGTERM)
            else:
                logger.info("File is there but the program is not running")
                logger.debug ("Removing lock file for the: %s as it can be there because of the program last time it was run" % old_pid_num)
        os.remove(pid_file)

    #Save current PID into file
    with open(pid_file, "w") as pf:
        pf.write("%s" % os.getpid())

def sigint_handler(loop, sig, frame):
    logger.info(f"Received signal {sig}")
    logger.info("Interrupt, stopping service")
    loop.quit()


def main():
    # Initialize logging
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG,
                        format='%(asctime)s - %(name)s %(levelname)s %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

    DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    arguments = parse_arguments()
    # Logging is set by default to WARN and higher.
    # With every occurrence of -v it's lowered by one
    logger.setLevel(max((3 - arguments.verbose) * 10, 0))

    bt_handler = BluetoothHandler(bus, arguments.address)
    loop = GLib.MainLoop()
    signal.signal(signal.SIGINT, partial(sigint_handler, loop))
    signal.signal(signal.SIGTERM, partial(sigint_handler, loop))

    if arguments.toggle:
        logger.info("Toggling bluetooth state")
        bt_handler.toggle_connection()
    elif arguments.power_off:
        logger.info("Power off and block bluetooth")
        bt_handler.power_off(True)
    elif arguments.listen:
        ensure_one_instance(SCRIPT_NAME)
        logger.info("Listening to events...")
        bt_handler.start_listen_loop()
        logger.info("Starting main loop...")
        loop.run()

    bt_handler.stop()
    bus.close()
    logger.info("Finished")

if __name__ == "__main__":
    main()
