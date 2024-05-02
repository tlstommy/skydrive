#!/usr/bin/env python3

#power_low_detector - monitors voltage and capacity of battery and shuts off when the values drop too low
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

from power_manager import PowerManager
import time
from subprocess import call

LOW_VOLTAGE_CUTOFF = 3.20
LOW_CAPACITY_CUTOFF = 20
CHECK_INTERVAL = 60

power_manager = PowerManager(1,0x36,LOW_VOLTAGE_CUTOFF)

def shutdown():
    print("Powering off...")
    
    call("sudo nohup shutdown -h now", shell=True)


while True:
    voltage = power_manager.get_battery_voltage()
    capacity = power_manager.get_battery_capacity()


    print("\nBattery Info:")
    print(f"Voltage:  {voltage}")
    print(f"Capacity: {capacity}")


    if(float(capacity) < 20):
        print("\nWarning: Low Battery!")
        print(f"Voltage:  {voltage}")
        print(f"Capacity: {capacity}")

    if(float(voltage) < LOW_VOLTAGE_CUTOFF):
        print("\nWarning: Low Voltage!")
        shutdown()

    if(float(capacity) < LOW_CAPACITY_CUTOFF):
        print("\nWarning: Low Capacity!")
        shutdown()    
    time.sleep(CHECK_INTERVAL)