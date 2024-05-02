#!/usr/bin/env python

#power_manager - power mangement program for geekworm x1202 i2c psu
#Copyright (C) 2024 Thomas Logan Smith

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <https://www.gnu.org/licenses/>.

import struct
import time
from subprocess import call

try:
    import smbus
    import gpiod
except ImportError as e:
    print("ImportError: ",e)
    

class PowerManager:
    def __init__(self,bus,target_address,voltage_cutoff):
        self.i2c_error = False
        try:
            self.i2c_bus = smbus.SMBus(bus)
        except Exception as e:
            print('Error :',e)
            self.i2c_error = True
        self.i2c_bus_address = target_address
        self.low_voltage_cutoff = voltage_cutoff
        
        

    def get_battery_voltage(self):
        if self.i2c_error:
            print("i2c error: voltage")
            return -1
        read = self.i2c_bus.read_word_data(self.i2c_bus_address, 2)
        swapped = struct.unpack("<H", struct.pack(">H", read))[0]
        bat_voltage = (((swapped * 1.25) / 1000) / 16)
        return  "%4.2f" % bat_voltage
    
    def get_battery_capacity(self):
        if self.i2c_error:
            print("i2c error: batterry")
            return -1

        read = self.i2c_bus.read_word_data(self.i2c_bus_address, 4)
        swapped = struct.unpack("<H", struct.pack(">H", read))[0]
        bat_cap = swapped/256
        return "%1i" % bat_cap

