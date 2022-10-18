#EB_32Conn.py

1) Scan for devices
2) Finds Service with UUID: 42D9FCD8E3684293BD6A22E694AE0CE0
3) Adds Mac address of devices that are advertising match Service to a list
4) Stops scanning after X seconds
5) Connects to all Matched devices on a round robin fashion
6) Writes 5 bytes to characteristic:C165393CF3374EFD8C8396226D85DE6E on Device
7) Reads 64 bytes(Poll) from characteristic: 3A4855F62F9C4005815BDF746358668E  
8) Does 6 and 7 on a round robin fashion to all connected devices
9) Stops the test after X Minutes

Paired with End Node described on: https://github.com/claudioasfilho/bt_AM_Conn_EN 