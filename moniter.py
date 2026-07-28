#!/usr/bin/env python3

from database import init_db, insert_to_health_metrics
from incidents.detector import check_and_record
import psutil
import time
import logging

logging.basicConfig(
    filename='moniter.log',
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def cpu_usage_in_percent():
    cpu_usage = psutil.cpu_percent(interval=1)
    if cpu_usage >= 90:
        health_status = "CRITICAL"
    elif cpu_usage >= 80:
        health_status = "WARNING"
    else:
        health_status = "HEALTHY"
    return cpu_usage, health_status


def total_disk_usage():
    disk = psutil.disk_usage("/")
    disk_usage = disk.percent
    if disk_usage >= 90:
        health_status = "CRITICAL"
    elif disk_usage >= 80:
        health_status = "WARNING"
    else:
        health_status = "HEALTHY"
    return disk_usage, health_status


def total_memory_usage():
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    if memory_usage >= 90:
        health_status = "CRITICAL"
    elif memory_usage >= 80:
        health_status = "WARNING"
    else:
        health_status = "HEALTHY"
    return memory_usage, health_status


init_db()

try:
    logger.info("Health monitor started")
    while True:
        cpu_usage, cpu_health = cpu_usage_in_percent()
        disk_usage, disk_health = total_disk_usage()
        memory_usage, memory_health = total_memory_usage()

        print(f"cpu_usage:    {cpu_usage}%  [{cpu_health}]")
        print(f"disk_usage:   {disk_usage}%  [{disk_health}]")
        print(f"memory_usage: {memory_usage}%  [{memory_health}]")
        print("-" * 50)

        for label, value, health in [
            ("CPU", cpu_usage, cpu_health),
            ("Disk Space", disk_usage, disk_health),
            ("Memory", memory_usage, memory_health),
        ]:
            msg = f"{label} usage: {value}% [{health}]"
            if health == "CRITICAL":
                logger.critical(msg)
            elif health == "WARNING":
                logger.warning(msg)
            else:
                logger.info(msg)

            # Runs once per metric per pass; the function itself decides
            # whether to create, ignore (already open), or resolve
            check_and_record(label, value)

        insert_to_health_metrics(cpu_usage, disk_usage, memory_usage)
        time.sleep(10)

except KeyboardInterrupt:
    print("\nMonitoring stopped by user with Ctrl+C. Goodbye!")
    logger.info("Health monitor stopped by user (KeyboardInterrupt)")