import json
import logging
import os
import timeit
import numpy as np
import datetime
from datetime import timedelta
import time
from collections import defaultdict

from sgp4.api import Satrec, jday
from sgp4 import omm
from skyfield.api import load, EarthSatellite, wgs84
from math import radians, sin, cos, sqrt, atan2

from config import ROOT_DIR


# Calculate distance between two points
def haversine_distance(lat1, lon1, lat2, lon2, radius=6371):
    # Convert latitude and longitude to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    # Calculate differences in latitude and longitude
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    # Calculate intermediate variables
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    # Calculate distance in kilometers
    distance = radius * c
    return distance


def load_tle_skyfield(path, group='iridium', data_format='tle', data_url=None):
    if not data_url:
        data_url = f'https://celestrak.org/NORAD/elements/gp.php?GROUP={group}&FORMAT={data_format}'

    filename = '.'.join([group, data_format])
    satellites = load.tle_file(data_url, filename=os.path.join(path, filename))

    return satellites


def import_data_json(path):
    if os.path.isfile(path):
        with open(path, 'r') as read_file:
            data_json = json.load(read_file)
        return data_json
    return None


def import_data_tle(path):
    tle = {}
    if os.path.isfile(path):
        with open(path, 'r') as read_file:
            content = read_file.read().splitlines()

        i = 0
        while i < len(content):
            satname = content[i].split(' ')[1]
            tle[satname] = [content[i + 1], content[i + 2]]
            i += 3

        return tle
    return None


def import_data_csv(path):
    if os.path.isfile(path):
        with open(path, 'r') as read_file:
            data_csv = next(omm.parse_csv(read_file))
        return data_csv
    return None


def save_data_json(path, data) -> None:
    """Updates the config .json file 'config' in 'path'."""
    with open(path, 'w') as f:
        json.dump(data, f)


if __name__ == '__main__':
    # log section
    LOG_PATH = os.path.join(ROOT_DIR, 'logs', 'iridium.log')
    WORK_PATH = os.path.join(ROOT_DIR, 'data')

    logFormatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.DEBUG)

    fileHandler = logging.FileHandler(LOG_PATH)
    fileHandler.setFormatter(logFormatter)
    fileHandler.setLevel(logging.DEBUG)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    consoleHandler.setLevel(logging.DEBUG)

    rootLogger.addHandler(fileHandler)
    rootLogger.addHandler(consoleHandler)

    # load data from celestrak
    # iridium_data = load_tle_skyfield(WORK_PATH, group='iridium-NEXT')

    # iridium.json
    config_path = os.path.join(WORK_PATH, 'iridium-NEXT.tle')
    iridium_data = import_data_tle(config_path)
    # iridium_data = iridium_data["102"]

    st = time.time()

    iridium_next_tle_modification_date = os.path.getmtime(os.path.join(WORK_PATH, 'iridium-NEXT.tle'))
    simulation_timestamp_gmt = time.gmtime(iridium_next_tle_modification_date)

    iridium_next_orbitals = import_data_json(os.path.join(WORK_PATH, 'iridium_next.orbitals.json'))

    curr_pos = [55.803890250, 37.407780570]

    year = simulation_timestamp_gmt.tm_year
    month = simulation_timestamp_gmt.tm_mon
    day = simulation_timestamp_gmt.tm_mday
    hour = simulation_timestamp_gmt.tm_hour
    minute = simulation_timestamp_gmt.tm_min
    second = simulation_timestamp_gmt.tm_sec

    optimal_distance_and_time = {}
    eph = load('de421.bsp')
    ts = load.timescale()

    for i in iridium_next_orbitals:
        k = 0
        curr_sat = str(iridium_next_orbitals[i][0])
        satellite = EarthSatellite(iridium_data[curr_sat][0], iridium_data[curr_sat][1])
        t = ts.utc(year, month, day, hour, minute, second)
        while k < 86400:
            t += timedelta(seconds=1)
            geocentric = satellite.at(t)
            lat, lon = wgs84.latlon_of(geocentric)

            satellite_distance = haversine_distance(curr_pos[0], curr_pos[1], lat.degrees, lon.degrees)
            dt = t.utc_datetime().timestamp()

            if not optimal_distance_and_time.get(i):
                optimal_distance_and_time[i] = [satellite_distance, dt, lat.degrees, lon.degrees]
            else:
                if optimal_distance_and_time[i][0] > satellite_distance:
                    optimal_distance_and_time[i] = [satellite_distance, dt, lat.degrees, lon.degrees]

            k += 1

    et = time.time()

    # get the execution time
    elapsed_time = et - st
    print('Execution time:', elapsed_time, 'seconds')

    print(optimal_distance_and_time)
    save_data_json(os.path.join(ROOT_DIR, 'results', 'data.json'), optimal_distance_and_time)
    # # Define the time for which you want to calculate the position
    # year = 2023
    # month = 5
    # day = 2
    # hour = 7
    # minute = 40
    # second = 0
    # microsecond = 0

    # satellite = Satrec.twoline2rv(iridium_data[0], iridium_data[1])
    # jd, fr = jday(year, month, day, hour, minute, second)
    # e, r, v = satellite.sgp4(jd, fr)
    # print('sgp4:', r)
    # # print(v)

    # satellite1 = EarthSatellite(iridium_data[0], iridium_data[1])
    # # Load the Earth ephemeris and the satellite TLE data
    # ts = load.timescale()
    # eph = load('de421.bsp')
    # t = ts.utc(year, month, day, hour, minute, second)
    # geocentric = satellite1.at(t)
    # print('skyfield:', geocentric.position.km)
    #
    # lat, lon = wgs84.latlon_of(geocentric)
    # height = wgs84.height_of(geocentric)
    # print(lat.degrees, ',', lon.degrees)
    # print('Height:', height)

    # curr_pos = [55.803890250, 37.407780570]
    # rootLogger.info(iridium_data[0])
