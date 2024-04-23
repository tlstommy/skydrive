import struct

import time
from subprocess import call

try:
    import smbus
    import gpiod
except ImportError as e:
    print("ImportError: ",e)
    

#power-management driver program for geekworm x1202

class PowerManager:
    def __init__(self,bus,target_address,voltage_cutoff):
        self.i2c_error = False
        try:
            self.i2c_bus = smbus.SMBus(bus)
        except Exception as e:
            print('Error :',e)
            self.i2c_error = True
        self.i2c_bus_address = target_address
        self.i2c_bus_address = voltage_cutoff
        
        
        

    def get_battery_voltage(self):
        if self.i2c_error:
            return -1

        read = self.i2c_bus.read_word_data(self.i2c_bus_address, 2)
        swapped = struct.unpack("<H", struct.pack(">H", read))[0]
        bat_voltage = (((swapped * 1.25) / 1000) / 16)
        return  "%4.2f" % bat_voltage
    
    def get_battery_capacity(self):
        if self.i2c_error:
            return -1

        read = self.i2c_bus.read_word_data(self.i2c_bus_address, 4)
        swapped = struct.unpack("<H", struct.pack(">H", read))[0]
        bat_cap = swapped/256
        return "%1i" % bat_cap

