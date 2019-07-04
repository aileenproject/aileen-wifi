import os
import logging
from typing import Tuple

from airo_tasks.utils import find_interface
from airo_tasks.start_airodump import start
from airo_tasks.watch_airodump_csv import read_airodump_csv_and_return_df
import settings


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def check_preconditions():
    """ check if we can find the network interface to monitor """
    logger.info("Checking preconditions ...")
    find_interface(settings.WIFI_INTERFACES)


def start_sensing(tmp_path: str = None):
    """ Start the airomon daemon """
    out_path = os.path.join(tmp_path, settings.AIRODUMP_FILE_PREFIX)
    
    wifi_interface_used = start(
        settings.SUDO_PWD,
        settings.FULL_PATH_TO_AIRMON_NG,
        settings.FULL_PATH_TO_AIRODUMP,
        out_path,
        settings.WIFI_INTERFACES,
        settings.AIRODUMP_LOG_INTERVAL_IN_SECONDS,
    )
    logger.info(
        "Started airodump listening on %s, writing to %s ..."
        % (wifi_interface_used, out_path)
    )


def get_latest_reading_as_df(tmp_path: str = None):
    """
    Return the latest reading in the dataframe format required by Aileen-core.
    (A dataframe with columns=["observable_id", "time_seen", "value", "observations"])
    Will ignore readings with too little power.
    """
    df = read_airodump_csv_and_return_df(
        tmp_path, settings.AIRODUMP_FILE_PREFIX, settings.AIRODUMP_MIN_POWER
    )
    df = df.rename(columns={"device_id": "observable_id"})
    df = df.rename(columns={"device_power": "value"})
    # collect observations
    obs_names = ["access_point_id", "total_packets", "access_point_id"]
    obs_vals = df[obs_names].T.to_dict()
    df["Mapper"] = df.index
    df = (
        df.assign(observations=df.Mapper.map(obs_vals))
        .drop("Mapper", 1)
        .drop(obs_names, 1)
    )
    return df


def adjust_event(
    event_value: int,
    last_event_value: int,
    observations: dict,
    last_observations: dict,
    device,
) -> Tuple[int, dict]:
    """
    Adjust event data dynamically, if needed.
    Returns updated event value and observations.
    Here, we compute the packet count per event (airodump records totals over time).
    """
    # We need some way to determine the correct amount of packets that were captured.
    # Reason: There is a possibility that the airodump-ng csv file had to restart.
    # Therefore, we need to check if this is a continuation of the airodump csv or if it is new.
    if last_event_value is None:
        # This device has not been recorded yet, so packet count is okay.
        observations["event_packets"] = observations.total_packets
        return event_value, observations
    new_total_packets = int(observations.total_packets)
    last_total_packets = int(last_observations.total_packets)
    if last_total_packets < new_total_packets:
        packets_for_this_event = new_total_packets - last_total_packets
    else:
        # Device exists in our records, but airomon restarted, so the package count is correct
        packets_for_this_event = new_total_packets

    observations["event_packets"] = new_total_packets
    return event_value, observations
