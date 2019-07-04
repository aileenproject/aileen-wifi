#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional
import logging

from netifaces import interfaces as net_interfaces

from airo_tasks.utils import find_interface, run_cmd_and_check_response
import settings


logger = logging.getLogger(__name__)


def put_wifi_interface_in_monitor_mode(
    interface: str, path_to_airmon_ng: str, sudo_pwd: str = None
) -> str:
    """Run airmon-ng on this wifi interface. Airmon-ng usually changes the name, so we return the new one."""
    interfaces_before = net_interfaces()
    run_cmd_and_check_response(
        "%s start %s" % (path_to_airmon_ng, interface),
        "PHY",
        # ["processes that could cause trouble", "Run it as root"],
        ["Run it as root"],
        sudo_pwd,
    )
    interfaces_after = net_interfaces()
    # check if there is a difference in the two lists
    if set(interfaces_before) == set(interfaces_after):
        return interface
    else:
        return list(set(interfaces_after) - set(interfaces_before))[0]


def start_airodump(
    interface: str,
    path_to_airodump_ng: str,
    airodump_file_name_prefix: str,
    log_interval_in_seconds: int,
    sudo_pwd,
):
    """Start airodump, in a mode that writes csv each n seconds."""
    command = "%s %s -w %s --output-format csv --write-interval %d" % (
        path_to_airodump_ng,
        interface,
        airodump_file_name_prefix,
        log_interval_in_seconds,
    )
    run_cmd_and_check_response(
        command, "BSSID", ["No such device", "Operation not permitted"], sudo_pwd
    )


def start(
    sudo_pwd,
    airmon_ng_path,
    airodump_path,
    airodump_file_prefix,
    wifi_interfaces,
    airodump_log_interval_in_seconds,
) -> Optional[str]:
    """Start airodump, be sure airomon monitors the right interface beforehand.
    Return interface name actually being used."""
    wifi_interface = None
    try:
        wifi_interface = find_interface(wifi_interfaces.split(","))
        wifi_interface = put_wifi_interface_in_monitor_mode(
            wifi_interface, airmon_ng_path, sudo_pwd
        )
        logging.info(
            "%s Monitor mode activated for wifi interface: '%s'"
            % (settings.TERM_LBL, wifi_interface)
        )
        start_airodump(
            wifi_interface,
            airodump_path,
            airodump_file_prefix,
            airodump_log_interval_in_seconds,
            sudo_pwd,
        )
    except KeyboardInterrupt:
        logging.error("%s KeyboardInterrupt!" % settings.TERM_LBL)
        exit(1)
    except Exception as e:
        logging.error("%s Problem: %s" % (settings.TERM_LBL, e))
        exit(2)
    return wifi_interface
