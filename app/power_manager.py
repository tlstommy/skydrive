import struct
import smbus
import time
from subprocess import call
import gpiod


#power-management driver program for geekworm x1202

class PowerManager:
    def __init__(self,bus,target_address,voltage_cutoff):
        self.i2c_bus = smbus.SMBus(bus)
        self.i2c_bus_address = target_address
        self.low_voltage_cutoff = voltage_cutoff
        

    def get_battery_voltage(self):
        read = self.i2c_bus.read_word_data(self.i2c_bus_address, 2)
        swapped = struct.unpack("<H", struct.pack(">H", read))[0]
        bat_voltage = (((swapped * 1.25) / 1000) / 16)
        return bat_voltage
    
    def get_battery_capacity(self):
        read = self.i2c_bus.read_word_data(self.i2c_bus_address, 4)
        swapped = struct.unpack("<H", struct.pack(">H", read))[0]
        bat_cap = swapped/256
        return bat_cap




    