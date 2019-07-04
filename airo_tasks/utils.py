from typing import List
import pexpect
from getpass import getuser
import logging

from netifaces import interfaces as net_interfaces

import settings

logger = logging.getLogger(__name__)


def run_cmd_and_check_response(
    command: str,
    success_match: str,
    failure_matches: List[str],
    sudo_pwd: str = None,
    timeout: int = 5,
) -> bool:
    """This method uses pexpect to talk us through a process interaction and checks the response.
    Optionally adds a sudo interaction beforehand."""
    if sudo_pwd is not None and sudo_pwd != "":
        logger.debug("%s Attempting to run command\"%s\" with sudo." % (settings.TERM_LBL, command))
        child = pexpect.spawn("sudo %s" % command, timeout=timeout)
        index = child.expect(["password for %s:" % getuser(), pexpect.TIMEOUT])
        if index > 0:
            print("Expected sudo password prompt, which did not appear it seems.")
            return False
        child.sendline(sudo_pwd)
    else:
        child = pexpect.spawn(command, timeout=5)
    index = child.expect(
        [success_match, *failure_matches, pexpect.EOF, pexpect.TIMEOUT], timeout=timeout
    )
    if index == 0:
        print(child.before, end=" ")
        child.interact()
    elif index <= len(failure_matches):
        logger.error(
            "%s Problem running command %s: %s"
            % (settings.TERM_LBL, command, failure_matches[index - 1])
        )
        return False
    else:
        logger.error(
            "%s Problem running command %s: No expected reply."
            % (settings.TERM_LBL, command)
        )
        return False
    return True


def find_interface(interfaces: List[str], escalate: bool = True) -> str:
    """Find out if one of the possible network interfaces is indeed present.
    Return the first one found or exit (with a message) if none can be found.
    We are trying to deal with a renaming that Airmon sometimes does (adding "mon")
    Attention: Airmon tends to completely rename interfaces, too, so it makes sense to check both
               original factory name and airmon-edited name. This is why the parameter is a list."""
    found_interface = None
    if not isinstance(interfaces, list):
        interfaces = str(interfaces).split(",")
    for interface in interfaces:
        if interface not in net_interfaces():
            # Try to see if the interface was already put into monitoring mode. Airmon renames it then.
            monitoring_interface = interface + "mon"
            if monitoring_interface in net_interfaces():
                logger.warning(
                    '%s interface %s does not exist, but with "mon" added it does.'
                    % (settings.TERM_LBL, interface)
                )
                found_interface = monitoring_interface
        else:
            found_interface = interface
    if found_interface is None and escalate:
        logger.error(
            "%s Error: the interfaces you specified (%s) cannot be found. Available interfaces: %s\n Maybe tweak the setting WIFI_INTERFACES ..."
            % (settings.TERM_LBL, interfaces, net_interfaces())
        )
        exit(2)
    return found_interface
