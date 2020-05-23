#!/usr/bin/env python3
import signal
import dbus
from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop
from bluetooth.ble import GATTRequester
from bluepy import btle
import subprocess
import argparse
import logging
import json
import sys
import time
import threading

logger = logging.getLogger(__name__)

class BluetoothHandler(btle.DefaultDelegate):
    BATTERY_UUID="00002a19-0000-1000-8000-00805f9b34fb"

    def __init__(self, bus, address):
        btle.DefaultDelegate.__init__(self)
        self.address = address
        self.address_dbus = address.replace(":","_")
        self.battery = -1
        self.bus = bus
        self.ble_requester = GATTRequester(address, False)
        self.device_object = bus.get_object('org.bluez',
                       f'/org/bluez/hci0/dev_{self.address_dbus}')
        # Interface for interacting with the device (connect, disconnect...)
        self.device_iface = dbus.Interface(self.device_object,
            dbus_interface='org.bluez.Device1')
        
        # Interface for querying properties
        self.device_props_iface = dbus.Interface(self.device_object,
            dbus_interface='org.freedesktop.DBus.Properties')
        logger.debug(f"{self.device_object}")

        self.subscribe_properties_changed()
        self.is_connected = self.get_device_property("Connected")
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
            self.on_connection_changed(bool(response["properties"]["Connected"]))
            has_changes = True

        if has_changes:
            self.print_status()

    def on_connection_changed(self, is_connected):
        self.is_connected = is_connected
        logger.info(f"Connection status changed to {self.is_connected}")
        if is_connected:
            self.start_read_battery_thread()

    def get_device_property(self, prop_name):
        prop_value = self.device_props_iface.Get("org.bluez.Device1",prop_name)
        logger.debug(f"Property value is: {prop_value}")
        return prop_value

    def subscribe_properties_changed(self):
        logger.info("Subscribing to property changes")
        #self.device_iface.connect_to_signal("PropertiesChanged",self.properties_changed_handler)
        self.bus.add_signal_receiver(self.properties_changed_handler,
            bus_name='org.bluez',
            #interface_keyword='interface',
            #member_keyword='member',
            path_keyword='path',
            #message_keyword='msg',
            signal_name="PropertiesChanged")

    def connect(self):
        if not self.is_connected:
            self.device_iface.Connect()
        else:
            logger.info("Already connected to device")

    def battery_notifications_loop(self):
        logger.info("--Starting battery notification handler...")
        p = btle.Peripheral(self.address)
        p.setDelegate(self)

        logger.info("Listening for battery notifications")
        while self.is_connected:
            try:
                p.waitForNotifications(5)
            except Exception as e:
                logger.error(f"Error while waiting for bat. notification {e}")
                pass

        logger.info("--Stopped listening for battery notifications")
        p.disconnect()

#    def read_device_battery(self):
#        logger.debug("Reading battery status...")
#        #self.ble_requester = GATTRequester(self.address, True)
#        #try:
#        self.ble_requester.connect(False)
#        while not self.ble_requester.is_connected():
#            time.sleep(0.5)

        #except RuntimeError:
        #    # Ignore, only given since the script isn't ran with privileges, however
        #    # they are not required and this can be safely ignored.
        #    logger.debug("Ignoring Runtime exception launched on Connect...")
        #    pass

#        self.battery = ord(self.ble_requester.read_by_uuid(self.BATTERY_UUID)[0])
#        logger.info(f"Battery is at: {self.battery}%")
#
#        try:
#            self.ble_requester.disconnect()
#        except Exception:
#            logger.debug("Exception")
#
#        return True

    def print_status(self):
        logger.info('Writing changes to console')
    
        output = {'text': f"{self.is_connected}-{self.battery}%",
                  'class': 'custom-bt-headphone'}
        logger.debug(json.dumps(output))
    
        sys.stdout.write(json.dumps(output) + '\n')
        sys.stdout.flush()

    def handleNotification(self, cHandle, data):
        logger.debug("Received notification from BLE")
        if cHandle == 45:
            new_bat = ord(data)
            logger.info(f"Received battery update, {new_bat}%")
            if self.battery != new_bat:
                self.battery = new_bat
                self.print_status()
        else:
            logger.debug("Received unknown notification from BLE")
            logger.debug(f"Handle: {cHandle}")
            logger.debug(f"Data: {ord(data)}")

#    def periodic_battery_update(self, time_interval_sec):
#        GLib.idle_add(self.read_device_battery, i)
#        logger.debug(f"Scheduling battery update each {time_interval_sec}seconds")
#        bat_thread = threading.Timer(time_interval_sec,self.read_device_battery)
#        bat_thread.daemon = True
#
#        bat_thread.start()
#                GLib.idle_add(lambda: next(gen, False), priority=GLib.PRIORITY_LOW)

def parse_arguments():
    parser = argparse.ArgumentParser()

    # Increase verbosity with every occurance of -v
    parser.add_argument('-v', '--verbose', action='count', default=0)

    # Define for which player we're listening
    #parser.add_argument('address')
    parser.add_argument('address', metavar='addr', type=str,
                    help='Bluetooth address of the headphones.')


    return parser.parse_args()

def main():
    DBusGMainLoop(set_as_default=True)
    signal.signal(signal.SIGINT, sigint_handler)
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

    logger.info("Starting main loop...")
    loop.run()


def sigint_handler(sig, frame):
    if sig == signal.SIGINT:
        sys.exit(1)
    else:
        raise ValueError("Undefined handler for '{}'".format(sig))

if __name__ == "__main__":
    main()
