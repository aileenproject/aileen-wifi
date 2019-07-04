import os

"""
Settings recognised by Aileen-Wifi.
Best to set them in an .env file, but just via bash export works.
"""


TRUTH_STRINGS = ["True", "true", "1", "t", "y", "yes"]

# The wifi interface names on which your device might sit.
# Factory identifier and maybe the one airmon uses after it ran. Use a comma-separated list for more than one.
WIFI_INTERFACES = os.environ.get("WIFI_INTERFACES", default="wlan1")
FULL_PATH_TO_AIRMON_NG = os.environ.get("FULL_PATH_TO_AIRMON_NG", default="airmon-ng")
FULL_PATH_TO_AIRODUMP = os.environ.get("FULL_PATH_TO_AIRODUMP", default="airodump-ng")
# This interval is how frequently we log monitored devices to file
AIRODUMP_LOG_INTERVAL_IN_SECONDS = int(
    os.environ.get("AIRODUMP_LOG_INTERVAL_IN_SECONDS", default=5)
)
# Use this as file prefix when airodump runs
AIRODUMP_FILE_PREFIX = "full_airodump_file"

# Minimal signal power needed to record an event. Look out: values are negative and bigger is better.
# Learn more at https://www.metageek.com/training/resources/understanding-rssi.html
AIRODUMP_MIN_POWER = os.environ.get("AIRODUMP_MIN_POWER", default=-70)

DISABLE_AUTO_TITLE = (
    os.environ.get("DISABLE_AUTO_TITLE", default="False") in TRUTH_STRINGS
)

SUDO_PWD = os.environ.get("SUDO_PWD", default="")

TERM_LBL = "[Aileen-Wifi]"

TIME_ZONE = os.environ.get("TIME_ZONE", "Europe/Amsterdam")

# This is a dict with labels of your choice as keys and observable IDs as values, e.g. {"hans": "4234q234q234"}.
DEBUG_DEVICES = {}
