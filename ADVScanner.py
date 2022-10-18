#!/usr/bin/env python3
"""
32 Connections example
"""

# Copyright 2021 Silicon Laboratories Inc. www.silabs.com
#
# SPDX-License-Identifier: Zlib
#
# The licensor of this software is Silicon Laboratories Inc.
#
# This software is provided 'as-is', without any express or implied
# warranty. In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.

import argparse
import os.path
import sys
import datetime
import time
from datetime import date, datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from common.util import BluetoothApp, find_service_in_advertisement, PeriodicTimer

# Constants

MANUFACTURE_ID = b"\xaa\xaa"
CUSTOM_SERVICE = b"\xe0\x0c\xae\x94\xe6\x22\x6a\xbd\x93\x42\x68\xe3\xd8\xfc\xd9\x42"#b"\x09\x18"
CUSTOM_CHAR = b"\x8e\x66\x58\x63\x74\xdf\x5b\x81\x05\x40\x9c\x2f\xf6\x55\x48\x3a"#b"\x1c\xa"

ADV_HEADER = b"\x02\x01\x06\x05\xff\xaa\xaa"

TURN_ON_GPIO = b"\x01\x01\x01"

# The maximum number of connections has to match with the configuration on the target side.
SL_BT_CONFIG_MAX_CONNECTIONS = 32


TIMER_PERIOD = 15.0
SCANNING_PERIOD = 5.0
SETTLING_PERIOD = 30.0


connectable_device = []
connectable_device_objects = []
custom_beacon_device_addresses = []
device_addresses = []
init_time = []
TX_Counter = []


class Connectable_device:
    def __init__(self, address, address_type, bonding, primary_phy, secondary_phy, adv_sid, tx_power, rssi):
        self.address = address
        self.address_type = address_type
        self.bonding = bonding
        self.primary_phy = primary_phy
        self.secondary_phy = secondary_phy
        self.adv_sid = adv_sid
        self.tx_power = tx_power
        self.rssi = rssi


class App(BluetoothApp):
    timerCounter = 0
    activeConnection = Connectable_device(0,0,0,0,0,0,0,0)
    connectionHandleCnt = 0
    connectionsMadeCnt = 0
    connAvailable = 0
    devices_found = 0
    Notification_Handler = 0
    scanner_initial_time = 0
    initial_time = 0
    scan_started = 0


    """ Application derived from generic BluetoothApp. """
    def event_handler(self, evt):
        """ Override default event handler of the parent class. """
        # This event indicates the device has started and the radio is ready.
        # Do not call any stack command before receiving this boot event!
        if evt == "bt_evt_system_boot":

            # Set passive scanning on 1Mb PHY
            #self.lib.bt.scanner.set_mode(1, SCAN_PASSIVE)
            # Set scan interval and scan window
            #self.lib.bt.scanner.set_timing(self.lib.bt.gap.PHY_PHY_1M, SCAN_INTERVAL, SCAN_WINDOW)
            # Set the default connection parameters for subsequent connections

         # Start scanning - looking for thermometer devices


        #  sl_bt_user_message_to_target(TURN_ON_GPIO)

            
            self.lib.bt.scanner.start(
                self.lib.bt.gap.PHY_PHY_1M,
                self.lib.bt.scanner.DISCOVER_MODE_DISCOVER_GENERIC)
            self.lib.bt.user.message_to_target(TURN_ON_GPIO)
            self.scanner_initial_time = time.time()
            self.conn_state = "scanning"
            print(self.conn_state)
            self.timer = PeriodicTimer(period=TIMER_PERIOD, target=self.timer_handler)
            self.devices_data = {}
            self.timer.start()

        # This event is generated when an advertisement packet or a scan response
        # is received from a responder
        elif evt == "bt_evt_scanner_legacy_advertisement_report":
            # Parse advertisement packets
            if (ADV_HEADER in evt.data):
                #If custom Beacon is found, and not already added to the List, it will get added to the list
                if evt.address not in device_addresses:
                    
                    device_addresses.append(evt.address)
                    loc_init_time = time.time()
                    loc_delta = loc_init_time - self.scanner_initial_time
                    loc_counter = int(evt.data[7]<<8 | evt.data[8])
                    

                    self.devices_data[self.devices_found] = {}
                    self.devices_data[self.devices_found]["Device_Handler"] = self.devices_found
                    self.devices_data[self.devices_found]["Device_address"] = evt.address
                    self.devices_data[self.devices_found]["Time_of_Discovery"] = loc_init_time
                    self.devices_data[self.devices_found]["Time_to_Discover"] = loc_delta
                    self.devices_data[self.devices_found]["_1st_BLE_TX_Count"] = loc_counter
                    self.devices_data[self.devices_found]["RSSI"] = evt.rssi
                    self.devices_data[self.devices_found]["RX_Count"] = 1

                    record = []
                    record.append(loc_counter)
                    TX_Counter.append(record)
                    
                    
                    init_time.append(loc_init_time)
                    #TX_Counter.append(loc_counter)
                    print("Device found :" + str(evt.address) + " time to discover: " + str(loc_delta)+"s " + "TX Counter: " + str(loc_counter)+" \n")
                    self.devices_found +=1
                else :
                    loc_data_len = len(self.devices_data)
                    for x in self.devices_data:
                        if self.devices_data[x]["Device_address"] == evt.address:
                            loc_counter = int(evt.data[7]<<8 | evt.data[8])
                            self.devices_data[x]["RX_Count"] += 1
                            TX_Counter[x].append(loc_counter)
                            print("Device " + str(self.devices_data[x]["Device_address"]) + " RX_Count= " + str(self.devices_data[x]["RX_Count"]) + " Latest_BLE_TX_Count= " + str(loc_counter)+ "\n")
                            #print(TX_Counter)
                            #print("\n")
                    

                    
                    

    def timer_handler(self):
        print("*************************************************Timer Stamp *************************************************")
        # self.lib.bt.scanner.stop()
        # # print(self.timerCounter)
        # """ Timer Handler """
        # if self.timerCounter >= SCANNING_PERIOD and self.conn_state == "scanning":
        #     self.timerCounter = 0
        #     # Stops Scanning
        #     self.lib.bt.scanner.stop()
        #     print("Scanning Stopped")

           


# Script entry point.
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    # Instantiate the application.
    app = App(parser=parser)
    # Running the application blocks execution until it terminates.
    app.run()