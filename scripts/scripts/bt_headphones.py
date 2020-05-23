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

logger = logging.getLogger(__name__)

class BluetoothHandler(btle.DefaultDelegate):
    BATTERY_UUID="00002a19-0000-1000-8000-00805f9b34fb"

    def __init__(self, bus, address):
        btle.DefaultDelegate.__init__(self)
        self.address = address
        self.bus = bus
        self.address_dbus = address.replace(":","_")
        self.battery = -1
        self.device_object = bus.get_object('org.bluez',
                       f'/org/bluez/hci0/dev_{self.address_dbus}')
        # Interface for interacting with the device (connect, disconnect...)
        self.device_iface = dbus.Interface(self.device_object,
            dbus_interface='org.bluez.Device1')
        
        # Interface for querying properties
        self.device_props_iface = dbus.Interface(self.device_object,
            dbus_interface='org.freedesktop.DBus.Properties')
        logger.debug(f"{self.device_object}")

        self.is_connected = self.get_device_property("Connected")

    def toggle_connection(self):
        if not self.is_connected:
            self.connect()
        else:
            self.disconnect()

    def start_listen_loop(self):
        self.subscribe_properties_changed()
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

        if "Connected" in response["properties"]:
            has_changes = self.on_connection_changed(bool(response["properties"]["Connected"]))

        if has_changes:
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
        prop_value = self.device_props_iface.Get("org.bluez.Device1",prop_name)
        logger.debug(f"Property {prop_name} value is: {prop_value}")
        return prop_value

    def subscribe_properties_changed(self):
        logger.info("Subscribing to property changes")
        self.bus.add_signal_receiver(self.properties_changed_handler,
            bus_name='org.bluez',
            path_keyword='path',
            signal_name="PropertiesChanged")

    def connect(self):
        if not self.is_connected:
            self.device_iface.Connect()
        else:
            logger.info("Already connected to device")

    def disconnect(self):
        if self.is_connected:
            self.device_iface.Disconnect()
        else:
            logger.info("No device to disconnect")

    def battery_notifications_loop(self):
        logger.info("--Starting battery notification handler...")
        self.btle_dev = btle.Peripheral(self.address)
        self.btle_dev.setDelegate(self)

        logger.info("Listening for battery notifications")
        while self.is_connected:
            try:
                self.btle_dev.waitForNotifications(5)
            except Exception as e:
                logger.error(f"Error while waiting for bat. notification {e}")
                pass

        logger.info("--Stopped listening for battery notifications")
        self.btle_dev.disconnect()

    def print_status(self):
        logger.info('Writing changes to console')
        output = {}
        if self.is_connected:
            icon = ""
            #Only send percentage is connected and available
            if self.battery != -1:
                output["percentage"] = self.battery
        else:
            icon = ""
        
        output["text"] = icon

        if "percentage" in output:
            if self.battery >= 60:
                bat_status = "good"
            elif self.battery >= 30:
                bat_status = "warning"
            else:
                bat_status = "critical"
        else:
            bat_status = "unknown"

        output["class"] = f"bat-{bat_status}"
                
        logger.debug(json.dumps(output))
    
        sys.stdout.write(json.dumps(output) + '\n')
        sys.stdout.flush()

    def handleNotification(self, cHandle, data):
        logger.debug("Received notification from BLE")
        if cHandle == 45:
            new_bat = ord(data)
            logger.info(f"Received battery update, new: {new_bat}% - old: {self.battery}")
            if self.battery != new_bat:
                self.battery = new_bat
                self.print_status()
        else:
            logger.debug("Received unknown notification from BLE")
            logger.debug(f"Handle: {cHandle}")
            logger.debug(f"Data: {ord(data)}")

    def stop(self):
        try:
            self.btle_dev.disconnect()
        except Exception:
            pass

def parse_arguments():
    parser = argparse.ArgumentParser()

    # Increase verbosity with every occurance of -v
    parser.add_argument('-v', '--verbose', action='count', default=0)

    parser.add_argument('--listen', action='store_true', help="Listen for connectivity and battery changes")
    parser.add_argument('--toggle', action='store_true', help="Toggle bluetooth connection")

    # Define for which player we're listening
    parser.add_argument('address', metavar='addr', type=str,
                    help='Bluetooth address of the headphones.')


    return parser.parse_args()

def main():
    DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    arguments = parse_arguments()
    # Initialize logging
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG,
                        format='%(name)s %(levelname)s %(message)s')
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

    if arguments.listen:
        logger.info("Listening to battery and connection events...")
        bt_handler.start_listen_loop()
        logger.info("Starting main loop...")
        loop.run()

    bt_handler.stop()
    bus.close()
    logger.info("Finished")


def sigint_handler(loop,sig, frame):
    logger.info(f"Received signal {sig}")
    logger.info("Interrupt, stopping service")
    loop.quit()

if __name__ == "__main__":
    main()
