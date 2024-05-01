#!/usr/bin/env python3

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