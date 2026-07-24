#!/usr/bin/env python3

import psutil
import time

Health_status = ''

def cpu_usage_in_percent(Health_status):
    cpu_usage = psutil.cpu_percent(interval=1)
    if cpu_usage > 90:
        Health_status = "CRITICAL"
    elif cpu_usage > 80:
        Health_status = "WARNING"
    else:
        Health_status = "HEALTHY"
    return cpu_usage, Health_status

def total_disk_usage(Health_status):
    disk = psutil.disk_usage("/")
    disk_usage = disk.percent
    
    if disk_usage > 90:
        Health_status = "CRITICAL"
    elif disk_usage > 80:
        Health_status = "WARNING"
    else:
        Health_status = "HEALTHY"
    return disk_usage, Health_status

def total_memory_usage(Health_status):
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    if memory_usage > 90:
        Health_status = "CRITICAL"
    elif memory_usage > 80:
        Health_status = "WARNING"
    else:
        Health_status = "HEALTHY"
    return memory_usage, Health_status


try:


    while True:
        cpu_usage, cpu_health = cpu_usage_in_percent(Health_status)
        disk_usage, disk_health = total_disk_usage(Health_status)
        memory_usage, memory_health = total_memory_usage(Health_status)


        print(f"cpu_usage:       {cpu_usage}%  {"[" + cpu_health + "]"}")
        print(f"disk_usage:     {disk_usage}%   {"[" + disk_health + "]"}")
        print(f"memory_usage:    {memory_usage}%  {"[" + memory_health + "]"}")
        print("-" * 50)
    
        time.sleep(10)  # Wait for 10 seconds before the next check
except KeyboardInterrupt:
    print("\nMonitoring stopped by user with Ctrl+C. Goodbye!")    




