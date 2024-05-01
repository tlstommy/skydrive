#!/usr/bin/env python
#This python script is only suitable for UPS Shield X1200, X1201 and X1202

import struct
import smbus
import time
from subprocess import call

def readVoltage(bus):

     address = 0x36
     read = bus.read_word_data(address, 2)
     swapped = struct.unpack("<H", struct.pack(">H", read))[0]
     voltage = swapped * 1.25 /1000/16
     return voltage


def readCapacity(bus):

     address = 0x36
     read = bus.read_word_data(address, 4)
     swapped = struct.unpack("<H", struct.pack(">H", read))[0]
     capacity = swapped/256
     return capacity


bus = smbus.SMBus(1)

while True:


        print ("Voltage:",readVoltage(bus))

        print ("Battery:",readCapacity(bus),"\n\n")
        time.sleep(0.5)

 
