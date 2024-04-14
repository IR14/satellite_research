from skyfield.api import Topos, load
from datetime import timedelta


def find_iridium_passes(observer_lat, observer_lon, tle_file):
    ts = load.timescale()
    tle_data = load.tle_file(tle_file)
    observer = Topos(latitude_degrees=observer_lat, longitude_degrees=observer_lon)

    passes = []
    for satellite in tle_data:
        t0, t1 = ts.now(), ts.now() + timedelta(days=1)
        t, events = satellite.find_events(observer, t0, t1, altitude_degrees=60)  # 30 градусов как пример
        rise_time = None
        for ti, event in zip(t, events):
            if event == 0:  # восход
                print(f'Satellite {satellite.name} rises at {ti.utc_datetime()}')
                rise_time = ti
            elif event == 1:  # кульминация
                print(f'Satellite {satellite.name} is at the highest point at {ti.utc_datetime()}')
            elif event == 2:  # заход
                print(f'Satellite {satellite.name} sets at {ti.utc_datetime()}')
                if rise_time is not None:
                    passes.append((rise_time, ti))

    return passes


# Загрузите TLE файл со спутниками Iridium
passes = find_iridium_passes(50.4501, 30.5234, 'data/iridium.tle')
