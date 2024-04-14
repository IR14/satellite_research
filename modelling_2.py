import numpy as np
from skyfield.api import Topos, load
from scipy.constants import kilo, mega, c
import matplotlib.pyplot as plt
import requests


# Загрузка TLE данных для спутников Iridium
def load_tle():
    url = "https://www.celestrak.com/NORAD/elements/iridium-NEXT.txt"
    response = requests.get(url)
    tle_lines = response.text.strip().splitlines()
    return [tle_lines[i:i + 3] for i in range(0, len(tle_lines), 3)]


# Расчет видимости спутников и атмосферного затухания
def satellite_visibility_and_attenuation(observer, tle_data, ts):
    satellites = load.tle(tle_data)
    t0 = ts.now()
    losses = []
    for name, satellite in satellites.items():
        t, events = satellite.find_events(observer, t0, t0 + 1, altitude_degrees=30)
        for ti, event in zip(t, events):
            if event == 1:  # Высшая точка
                # Расчет затухания
                elevation = observer.at(ti).observe(satellite).apparent().altaz()[1].degrees
                attenuation = basic_atmospheric_attenuation(elevation)
                losses.append((ti.utc_datetime(), attenuation))
    return losses


# Простая модель атмосферного затухания
def basic_atmospheric_attenuation(elevation_angle):
    # Более сложные модели могут учитывать погодные условия, влажность и другие факторы
    if elevation_angle > 45:
        return 0.5  # дБ
    else:
        return 1.5  # дБ из-за низкой элевации


# Визуализация затухания
def plot_attenuations(attenuations):
    times = [att[0] for att in attenuations]
    values = [att[1] for att in attenuations]
    plt.figure(figsize=(10, 5))
    plt.plot(times, values, marker='o', linestyle='-', color='blue')
    plt.title('Atmospheric Attenuation Over Time')
    plt.xlabel('Time')
    plt.ylabel('Attenuation (dB)')
    plt.grid(True)
    plt.show()


def main():
    observer = Topos('50.4501 N', '30.5234 E')
    ts = load.timescale()
    tle_data = load_tle()
    attenuations = satellite_visibility_and_attenuation(observer, tle_data, ts)
    plot_attenuations(attenuations)


if __name__ == "__main__":
    main()
