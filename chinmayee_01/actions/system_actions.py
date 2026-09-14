"""
System & OS Action Handlers
Handles time, date, battery status, CPU/RAM metrics, and system operations.
"""

import datetime
import os
import sys
import psutil
import config

logger = config.logger


def get_current_time(text: str, params: dict) -> str:
    """Returns formatted 12-hour local time."""
    now = datetime.datetime.now()
    formatted_time = now.strftime("%I:%M %p").lstrip("0")
    return f"The current time is {formatted_time}."


def get_current_date(text: str, params: dict) -> str:
    """Returns formatted day of the week and full date."""
    now = datetime.datetime.now()
    formatted_date = now.strftime("%A, %B %d, %Y")
    return f"Today is {formatted_date}."


def get_system_status(text: str, params: dict) -> str:
    """Queries CPU usage, memory utilization, and battery percentage."""
    try:
        cpu_usage = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory()
        battery = psutil.sensors_battery()

        status_msg = f"CPU usage is at {cpu_usage} percent. Memory usage is {ram.percent} percent."
        if battery:
            plugged_status = "plugged in" if battery.power_plugged else "on battery"
            status_msg += f" Battery is at {battery.percent} percent and {plugged_status}."
        return status_msg
    except Exception as e:
        logger.error(f"Error fetching system metrics: {e}")
        return "I was unable to retrieve complete system diagnostics."


def lock_workstation(text: str, params: dict) -> str:
    """Locks the operating system workstation screen."""
    try:
        if sys.platform == "win32":
            import ctypes
            ctypes.windll.user32.LockWorkStation()
            return "Locking your computer now."
        elif sys.platform == "darwin":
            os.system("/System/Library/CoreServices/Menu\\ Extras/User.menu/Contents/Resources/CGSession -suspend")
            return "Locking macOS session."
        else:
            os.system("xdg-screensaver lock")
            return "Locking Linux workstation."
    except Exception as e:
        logger.error(f"Failed to lock workstation: {e}")
        return "Unable to lock the workstation automatically."


def register_system_intents(intent_engine):
    """Registers all system-related intents with the engine."""
    intent_engine.register_intent(
        name="get_time",
        patterns=["what time is it", "current time", "what is the time", "tell me the time", "what's the time", "the time right now", "time right now", "time please", "the time", "time"],
        description="Provides the current local time.",
        requires_internet=False
    )(get_current_time)

    intent_engine.register_intent(
        name="get_date",
        patterns=["what day is today", "what is today's date", "what is the date", "current date", "tell me the date", "what's the date", "today's date", "what day is it", "which day is today", "today's day", "date today", "date"],
        description="Provides today's day and date.",
        requires_internet=False
    )(get_current_date)

    intent_engine.register_intent(
        name="system_status",
        patterns=["system status", "battery status", "cpu usage", "ram usage", "memory usage", "battery percentage", "battery", "device status", "system telemetry", "telemetry", "system diagnostics"],
        description="Reports current CPU, RAM, and Battery percentages.",
        requires_internet=False
    )(get_system_status)

    intent_engine.register_intent(
        name="lock_pc",
        patterns=["lock my computer", "lock screen", "lock workstation", "lock pc", "lock the screen", "lock computer"],
        description="Locks the user screen.",
        requires_internet=False
    )(lock_workstation)

