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
from datetime import date, datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
from common.conversion import Ieee11073Float
from common.util import BluetoothApp, find_service_in_advertisement, PeriodicTimer

# Constants
#CUSTOM_SERVICE = b"\xDE\x8A\x5A\xAC\xA9\x9B\xC3\x15\x0C\x80\x60\xD4\xCB\xB5\x12\x24"
CUSTOM_SERVICE = b"\xe0\x0c\xae\x94\xe6\x22\x6a\xbd\x93\x42\x68\xe3\xd8\xfc\xd9\x42"



#DE8A5AACA99BC3150C8060D4CBB51224
#de 8a 5a ac a9 9b c3 15 0c 80 60 d4 cb b5 12 24

ADV_HEADER = b"\x02\x01\x06\x11\x07\xE0\x0C\xAE\x94\xE6\x22\x6A\xBD\x93\x42\x68\xE3\xD8\xFC\xD9\x42"




CONN_INTERVAL_MIN = 10   # 100 ms
CONN_INTERVAL_MAX = 10   # 100 ms
CONN_SLAVE_LATENCY = 0   # no latency
CONN_TIMEOUT = 300       # 1000 ms
CONN_MIN_CE_LENGTH = 0
CONN_MAX_CE_LENGTH = 65535

SCAN_INTERVAL = 16       # 10 ms
SCAN_WINDOW = 16         # 10 ms
SCAN_PASSIVE = 0

# The maximum number of connections has to match with the configuration on the target side.
SL_BT_CONFIG_MAX_CONNECTIONS = 32


TIMER_PERIOD = 0.5
SECONDS_IN_TIMER_PERIOD = 5*TIMER_PERIOD

SCANNING_PERIOD = 5*SECONDS_IN_TIMER_PERIOD
SETTLING_PERIOD = 6*SECONDS_IN_TIMER_PERIOD


connectable_device = []
connectable_device_objects = []
connectable_device_addresses = []
init_time = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
final_time = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
payload_received = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
packets_received = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
receive_silence = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

class Connectable_device:
    def __init__(self, address, address_type, bonding, rssi):
        self.address = address
        self.address_type = address_type
        self.bonding = bonding
        self.rssi = rssi


class App(BluetoothApp):
    timerCounter = 0
    #activeConnection = Connectable_device(0,0,0,0,0,0,0,0)
    connectionHandleCnt = 0
    connectionsMadeCnt = 0
    connAvailable = 0
    Notification_Handler = 0
    initial_time = 0
    final_time = 0

    def contains(list, address):
        for x in list:
            if x.address == address:
                return True
            return False

    def createFile(self, connection, handler, address):
        original_stdout = sys.stdout # Save a reference to the original standard output
        with open('dataFromConn'+ str(connection) + '.txt', 'w') as f:
            sys.stdout = f # Change the standard output to the file we created
            print("Connection address: " + str(address) + "\n")
            print("Connection #: " + str(connection) + "\n")
            print("Connection handler#: " + str(handler) + "\n")
            # self.initial_time = datetime.now()
            # print(str(self.initial_time) + "\n")

        sys.stdout = original_stdout # Reset the standard output to its original value

    def appendFile(self, connection, handler, data):
        original_stdout = sys.stdout # Save a reference to the original standard output
        with open('dataFromConn'+ str(connection) + '.txt', 'a') as f:
            sys.stdout = f # Change the standard output to the file we created
            print(data)
            # self.final_time = datetime.now()
            # print(str(datetime.now()) + "\n")
        sys.stdout = original_stdout # Reset the standard output to its original value

    """ Application derived from generic BluetoothApp. """
    def event_handler(self, evt):
        """ Override default event handler of the parent class. """
        # This event indicates the device has started and the radio is ready.
        # Do not call any stack command before receiving this boot event!
        if evt == "bt_evt_system_boot":

            # # Set passive scanning on 1Mb PHY
            # self.lib.bt.scanner.set_mode(self.lib.bt.gap.PHY_PHY_1M, SCAN_PASSIVE)
            # # Set scan interval and scan window
            # self.lib.bt.scanner.set_timing(self.lib.bt.gap.PHY_PHY_1M, SCAN_INTERVAL, SCAN_WINDOW)
            # Set the default connection parameters for subsequent connections
            self.lib.bt.connection.set_default_parameters(
                CONN_INTERVAL_MIN,
                CONN_INTERVAL_MAX,
                CONN_SLAVE_LATENCY,
                CONN_TIMEOUT,
                CONN_MIN_CE_LENGTH,
                CONN_MAX_CE_LENGTH)
            # Start scanning - looking for thermometer devices
            self.lib.bt.scanner.start(
                self.lib.bt.gap.PHY_PHY_1M,
                self.lib.bt.scanner.DISCOVER_MODE_DISCOVER_GENERIC)
            self.conn_state = "scanning"
            self.last_conn_state = ""
            self.timer = PeriodicTimer(period=TIMER_PERIOD, target=self.connection_timer_handler)
            self.timer.start()
            self.conn_properties = {}
            self.connection_mtu = 0
            self.connection_payload = 0

        # This event is generated when an advertisement packet or a scan response
        # is received from a responder
        elif evt == "bt_evt_scanner_legacy_advertisement_report":
            print(evt.data)
            # Parse advertisement packets
            #if (ADV_HEADER in evt.data):
            if find_service_in_advertisement(evt.data, CUSTOM_SERVICE):
                #self.activeConnection= Connectable_device(evt.address,evt.address_type, evt.bonding,evt.rssi)
                if evt.address not in connectable_device_addresses:
                    connectable_device_addresses.append(evt.address)
                    print(len(connectable_device_addresses))

            # if evt.packet_type == 0:
            #     # If a thermometer advertisement is found...
            #     if find_service_in_advertisement(evt.data, CUSTOM_SERVICE):
            #         self.activeConnection= Connectable_device(evt.address,evt.address_type, evt.bonding, evt.primary_phy, evt.secondary_phy, evt.adv_sid, evt.tx_power, evt.rssi)
            #         if evt.address not in connectable_device_addresses:
            #             connectable_device_addresses.append(evt.address)
            #             # print(len(connectable_device_addresses))


        # This event indicates that a new connection was opened.
        elif evt == "bt_evt_connection_opened":
            print("\nConnection opened Address:" + str(evt.address))

            self.createFile(evt.connection, self.connectionHandleCnt, evt.address)


            self.connectionHandleCnt +=1
            self.connectionsMadeCnt +=1
            self.conn_properties[evt.connection] = {}
            # Only the last 3 bytes of the address are relevant
            self.conn_properties[evt.connection]["server_address"] = evt.address[9:].upper()

            if self.connectionsMadeCnt == self.connAvailable:
                self.conn_state = "Done_connecting"
                self.Notification_Handler = 1
            else:
                self.conn_state = "Connections_In_Progress"

            self.lib.bt.connection.set_preferred_phy(evt.connection, 2, 3)

        # This event is generated when a connection is dropped
        elif evt == "bt_evt_connection_closed":
            print("Connection closed:", evt.connection)
            #print("\nConnection closed Address:" + str(evt.address))
            del self.conn_properties[evt.connection]
            self.connectionHandleCnt -=1
            self.connectionsMadeCnt -=1

        elif evt == "bt_evt_gatt_mtu_exchanged":
            self.connection_mtu = evt.mtu
            self.connection_payload = self.connection_mtu - 5
            print("MTU set for connection ..." + str(evt.connection) + " as " + str(self.connection_mtu))
            print("Payload set for connection" + str(evt.connection) + " as " + str(self.connection_payload))

        elif evt == "bt_evt_gatt_procedure_completed":
            # If service discovery finished
            if self.conn_state == "Reading_and_writting":
                # Discover thermometer characteristic on the slave device
                print("Notifications enabled on connection# " + str(evt.connection))

        elif evt == "bt_evt_gatt_characteristic_value":
            if self.conn_state == "Reading_and_writting":
                #self.Notification_Handler = evt.connection

                if packets_received[evt.connection - 1] == 0 and evt.att_opcode == 0x1b:
                    self.initial_time = datetime.now()
                    init_time[evt.connection - 1] = self.initial_time
                    self.appendFile(evt.connection, self.connectionHandleCnt, self.initial_time)
                    print("Start logging time evt.connection" + str(evt.connection))

                self.final_time = datetime.now()
                # final_time.append(self.final_time)
                # print("evt.connection" + str(evt.connection))
                final_time[evt.connection - 1] = self.final_time
                self.appendFile(evt.connection, self.connectionHandleCnt, evt.value)
                payload_received[evt.connection - 1] += len(evt.value)
                packets_received[evt.connection - 1] += 1
                receive_silence[evt.connection - 1] = 0

    def connection_timer_handler(self):
        # print(self.timerCounter)
        """ Timer Handler """
        if self.timerCounter >= SCANNING_PERIOD and self.conn_state == "scanning":
            self.timerCounter = 0
            # Stops Scanning
            self.lib.bt.scanner.stop()
            print("Scanning Stopped, connecting to devices")
            self.conn_state = "Connecting_to_devices"
            print(connectable_device_addresses)
            print(connectable_device_objects)

        else:
            if self.conn_state == "scanning":
                self.timerCounter +=1

        if self.conn_state == "Connecting_to_devices":
            #It checks how many devices are availabe for Connection
            self.connAvailable = len(connectable_device_addresses)
            #In case the number of devices available is higher than SL_BT_CONFIG_MAX_CONNECTIONS
            #It will force to be SL_BT_CONFIG_MAX_CONNECTIONS
            if self.connAvailable > SL_BT_CONFIG_MAX_CONNECTIONS:
                self.connAvailable = SL_BT_CONFIG_MAX_CONNECTIONS

            print("Number of connectable devices " + str(self.connAvailable))
            #It initializes the counter for the connections
            self.connectionHandleCnt = 0
            self.conn_state = "Connections_In_Progress"

        if self.conn_state == "Connections_In_Progress":

            if self.connectionsMadeCnt < self.connAvailable:

                self.lib.bt.connection.open(connectable_device_addresses[self.connectionHandleCnt],0,self.lib.bt.gap.PHY_PHY_1M)
                self.conn_state = "opening_connection"
            # else:
            #     self.conn_state = "opening"
        if self.conn_state == "Done_connecting":
            self.timerCounter = 0
            self.conn_state = "Reading_and_writting"
            print("self.conn_state == Done_connecting " + str(self.Notification_Handler))

        if self.conn_state == "Reading_and_writting":
            if self.Notification_Handler <= self.connAvailable:

                payload_received [self.Notification_Handler - 1] = 0
                packets_received [self.Notification_Handler - 1] = 0

                # sl_bt_gatt_read_characteristic_value(1, 23)

                #self.lib.bt.gatt.set_characteristic_notification(self.Notification_Handler, 21, 1)

                self.lib.bt.gatt.read_characteristic_value(self.Notification_Handler, 23)
                self.Notification_Handler += 1

            i = 0
            while i < self.connAvailable:
                receive_silence[i] += 1
                if receive_silence[i] == 2:
                    connectionStamp = "Connection #" + str(i+1) + " silent \n"
                    self.appendFile(i+1, i+1, connectionStamp)
                    print( connectionStamp )
                i += 1


            if self.timerCounter == SETTLING_PERIOD: # in seconds when to write log time
                #print(final_time)
                #print(init_time)
                #print("self.connAvailable " + str(self.connAvailable))
                print("\nWritting Final Time to Files\n")
                i = 0
                while i < self.connAvailable:

                    connectionStamp = "Connection #" + str(i+1) + "\n" + "Final Time:" + str(final_time[i])
                    self.appendFile(i+1, i+1, connectionStamp)
                    print( connectionStamp )

                    if (final_time[i] != 0):


                        #self.appendFile(i+1, i+1, final_time[i])
                        delta = final_time[i] - init_time[i]

                        connectionStamp = "Final Time - Initial time = " + str(delta) + "\n" + \
                        "Payload Received = " + str(payload_received[i]) + " Bytes" + "\n" + \
                        "Packets Received = " + str(packets_received[i]) + "\n" + \
                        "Transfer speed in kbps: " + str(round( (payload_received[i] * 8) / delta.total_seconds()) / 1000)

                        self.appendFile(i+1, i+1, connectionStamp)

                        print( connectionStamp )
                        #self.appendFile(i+1,i+1, delta. )

                    i += 1
                    print( "\n" )



            self.timerCounter +=1

        if (self.conn_state != self.last_conn_state):
            print("\n*** STATE: ", self.conn_state, "\n")
            self.last_conn_state = self.conn_state

# Script entry point.
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    # Instantiate the application.
    app = App(parser=parser)
    # Running the application blocks execution until it terminates.
    app.run()
