from functools import wraps

import json
from common.huffman import Huffman


def log_test_func(func):
    @wraps(func)
    def wrapper_do_twice(*args, **kwargs):
        print(f'\n$ Вызов тест-функции: {func.__name__}')
        serialized_data, raw_size = func(*args, **kwargs)
        measure_compression(serialized_data, raw_size)

    return wrapper_do_twice


def calculate_size_in_bytes(data: bytes) -> int:
    result = len(data)
    print(f"Serialized size: {result} bytes")
    return result


def calculate_compressed_size(encoded_data: str) -> int:
    result = (len(encoded_data) + 7) // 8
    print(f"Compressed size: {result} bytes")
    return result


def calculate_compression_ratio(original_size: int, compressed_size: int) -> float:
    result = original_size / compressed_size
    return result


def calculate_json_size(json_str: str) -> int:
    json_obj = json.loads(json_str)
    serialized_json_str = json.dumps(json_obj, separators=(',', ':'))
    result = len(serialized_json_str.encode('utf-8'))
    print(f"JSON size: {result} bytes")
    return result


def measure_compression(serialized_data: bytes, raw_size: int) -> None:
    encoded_data, code_book = huffman.encode(serialized_data)
    decoded_data = huffman.decode(encoded_data, code_book)

    serialized_size = calculate_size_in_bytes(serialized_data)
    serialized_ratio = calculate_compression_ratio(raw_size, serialized_size)
    compressed_size = calculate_compressed_size(encoded_data)
    compression_ratio = calculate_compression_ratio(serialized_size, compressed_size)

    print("Encoded:", encoded_data)
    print("Decoded:", decoded_data)
    print(f"Compression ratio: {compression_ratio}")
    print(f"Serialization ratio: {serialized_ratio}")
    print(f'FINAL ratio JSON-S -> ENCODED {calculate_compression_ratio(raw_size, compressed_size)}')


@log_test_func
def test_iotj() -> [bytes, int]:
    from protobuf import iotj_pb2
    huffman = Huffman()

    json_string = """
    {
        "phyPayload":"this is an example of a huffman tree with extended dictionary capabilities",
        "rxInfo":{
            "channel":1,
            "codeRate":"4/5",
            "crcStatus":1,
            "dataRate": {
                "bandwidth":125,
                "modulation":"LORA",
                "spreadFactor":7
            },
            "frequency":868300000,
            "loRaSNR":7,
            "mac":"1dee08d0b691d149",
            "rfChain":1,
            "rssi":-57,
            "size":23,
            "time":"2023-02-17T01:29:00Z",
            "timestamp":1676586505
        }
    }
    """
    raw_size = calculate_json_size(json_string)

    pb = iotj_pb2.iotj()
    pb.rxinfo.channel = 1
    pb.rxinfo.codeRate = "4/5"
    pb.rxinfo.crcStatus = 1
    pb.rxinfo.dataRate.bandwidth = 125
    pb.rxinfo.dataRate.modulation = iotj_pb2.rate.LORA
    pb.rxinfo.dataRate.spreadFactor = 7
    pb.rxinfo.frequency = 868300000
    pb.rxinfo.loRaSNR = 7
    pb.rxinfo.mac = "1dee08d0b691d149"
    pb.rxinfo.rfChain = 1
    pb.rxinfo.rssi = -57
    pb.rxinfo.size = 23
    pb.rxinfo.time.FromJsonString("2024-04-13T12:00:00Z")
    pb.rxinfo.timestamp.FromSeconds(2074240683)
    pb.phyPayload = "this is an example of a huffman tree with extended dictionary capabilities"

    return pb.SerializeToString(), raw_size


@log_test_func
def test_iot_temp() -> [bytes, int]:
    from protobuf import iot_temp_pb2
    huffman = Huffman()

    json_string = """
    {
        "id":"__export__.temp_log_196134_bd201015",
        "room_id/id":"Room Admin",
        "noted_date":"08-12-2018 09:30",
        "temp":29,
        "out/in":"In"
    }
    """
    raw_size = calculate_json_size(json_string)

    pb = iot_temp_pb2.LogEntry()
    pb.entity = "__export__.temp_log_196134_bd201015"
    pb.user = "Room Admin"
    pb.timestamp.FromSeconds(2074240683)
    pb.temperature = 29
    pb.status = "In"

    return pb.SerializeToString(), raw_size


@log_test_func
def test_iot_temp_normal():
    from protobuf import iot_temp_pb2
    huffman = Huffman()

    json_string = """
    {
        "id":"__export__.temp_log_196134_bd201015",
        "room_id/id":"Room Admin",
        "noted_date":"08-12-2018 09:30",
        "temp":29,
        "out/in":"In"
    }
    """
    raw_size = calculate_json_size(json_string)

    message_source_map = {
        "__export__.temp_log_": "TEMP_LOG"
    }
    user_map = {
        "Room Admin": "ROOM_ADMIN"
    }
    pb = iot_temp_pb2.LogEntryNormal()
    pb.messageSource = message_source_map["__export__.temp_log_"]
    pb.tickHash = 196134
    pb.messageHash = int("bd201015", 16)
    pb.user = user_map["Room Admin"]
    pb.timestamp.FromSeconds(1712847600)
    pb.temperature = 29
    pb.status = "In"

    return pb.SerializeToString(), raw_size


@log_test_func
def test_beach_water():
    from protobuf import beach_water_pb2
    huffman = Huffman()

    json_string = """
    {
        "Beach Name":"Montrose Beach",
        "Measurement Timestamp":"08/30/2013 08:00:00 AM",
        "Water Temperature":20.3,
        "Turbidity":1.18,
        "Transducer Depth":0.891,
        "Wave Height":0.08,
        "Wave Period":3.0,
        "Battery Life":9.4,
        "Measurement Timestamp Label":"8/30/2013 8:00 AM",
        "Measurement ID":"MontroseBeach201308300800"
    }
    """
    raw_size = calculate_json_size(json_string)

    pb = beach_water_pb2.WaterMetrics()
    pb.beach = 'Montrose Beach'
    pb.timestamp = "08/30/2013 08:00:00 AM"
    pb.temperature = 20.3
    pb.turbidity = 1.18
    pb.transducer_depth = 0.891
    pb.wave_height = 0.08
    pb.wave_period = 3.0
    pb.battery_life = 9.4
    pb.timestamp_m = "8/30/2013 8:00 AM"
    pb.id = 'MontroseBeach201308300800'

    return pb.SerializeToString(), raw_size


@log_test_func
def test_beach_water_normal():
    from protobuf import beach_water_pb2
    huffman = Huffman()

    json_string = """
    {
        "Beach Name":"Montrose Beach",
        "Measurement Timestamp":"08/30/2013 08:00:00 AM",
        "Water Temperature":20.3,
        "Turbidity":1.18,
        "Transducer Depth":0.891,
        "Wave Height":0.08,
        "Wave Period":3.0,
        "Battery Life":9.4,
        "Measurement Timestamp Label":"8/30/2013 8:00 AM",
        "Measurement ID":"MontroseBeach201308300800"
    }
    """
    raw_size = calculate_json_size(json_string)

    beach_map = {
        'Montrose Beach': 'MONTROSE_BEACH',
        'Ohio Street Beach': 'OHIO_STREET_BEACH',
        'Calumet Beach': 'CALUMET_BEACH',
        '63rd Street Beach': 'STREET_BEACH_63RD',
        'Osterman Beach': 'OSTERMAN_BEACH',
        'Rainbow Beach': 'RAINBOW_BEACH'
    }
    user_map = {
        "Room Admin": "ROOM_ADMIN"
    }
    pb = beach_water_pb2.WaterMetricsNormal()
    pb.beach = beach_map['Montrose Beach']
    pb.timestamp.FromSeconds(1712847600)
    pb.temperature = 20.3
    pb.turbidity = 1.18
    pb.transducer_depth = 0.891
    pb.wave_height = 0.08
    pb.wave_period = 3.0
    pb.battery_life = 9.4
    pb.id = 8

    return pb.SerializeToString(), raw_size


@log_test_func
def test_beach_weather():
    from protobuf import beach_weather_pb2
    huffman = Huffman()

    json_string = """
    {
        "Station Name":"Oak Street Weather Station",
        "Measurement Timestamp":"05/22/2015 03:00:00 PM",
        "Air Temperature":10.3,
        "Wet Bulb Temperature":7.0,
        "Humidity":55.0,
        "Rain Intensity":0.0,
        "Interval Rain":0.0,
        "Total Rain":1.4,
        "Precipitation Type":0.0,
        "Wind Direction":63.0,
        "Wind Speed":1.9,
        "Maximum Wind Speed":2.8,
        "Barometric Pressure":2.3,
        "Solar Radiation":780.0,
        "Heading":322.0,
        "Battery Life":12.0,
        "Measurement Timestamp Label":"05/22/2015 3:00 PM",
        "Measurement ID":"OakStreetWeatherStation201505221500"}
    """
    raw_size = calculate_json_size(json_string)

    pb = beach_weather_pb2.BeachWeatherMetrics()
    pb.station_name = "Oak Street Weather Station"
    pb.measurement_timestamp = "05/22/2015 03:00:00 PM"
    pb.air_temperature = 10.3
    pb.wet_bulb_temperature = 7.0
    pb.humidity = 55.0
    pb.rain_intensity = 0.0
    pb.interval_rain = 0.0
    pb.total_rain = 1.4
    pb.precipitation_type = 0.0
    pb.wind_direction = 63.0
    pb.wind_speed = 1.9
    pb.maximum_wind_speed = 2.8
    pb.barometric_pressure = 780.0
    pb.heading = 322.0
    pb.battery_life = 12.0
    pb.measurement_timestamp_label = "05/22/2015 3:00 PM"
    pb.measurement_id = 'OakStreetWeatherStation201505221500'

    return pb.SerializeToString(), raw_size


@log_test_func
def test_beach_weather_normal():
    from protobuf import beach_weather_pb2
    huffman = Huffman()

    json_string = """
    {
        "Station Name":"Oak Street Weather Station",
        "Measurement Timestamp":"05/22/2015 03:00:00 PM",
        "Air Temperature":10.3,
        "Wet Bulb Temperature":7.0,
        "Humidity":55.0,
        "Rain Intensity":0.0,
        "Interval Rain":0.0,
        "Total Rain":1.4,
        "Precipitation Type":0.0,
        "Wind Direction":63.0,
        "Wind Speed":1.9,
        "Maximum Wind Speed":2.8,
        "Barometric Pressure":2.3,
        "Solar Radiation":780.0,
        "Heading":322.0,
        "Battery Life":12.0,
        "Measurement Timestamp Label":"05/22/2015 3:00 PM",
        "Measurement ID":"OakStreetWeatherStation201505221500"}
    """
    raw_size = calculate_json_size(json_string)

    station_map = {
        'Oak Street Weather Station': 'OAK_STREET_WEATHER_STATION',
        'Foster Weather Station': 'FOSTER_WEATHER_STATION',
        '63rd Street Weather Station': 'STATION_WEATHER_STREET_63RD',
    }
    pb = beach_weather_pb2.BeachWeatherMetricsNormal()
    pb.station_name = station_map["Oak Street Weather Station"]
    pb.measurement_timestamp.FromSeconds(1432306800)
    pb.air_temperature = 10.3
    pb.wet_bulb_temperature = 7.0
    pb.humidity = 55.0
    pb.rain_intensity = 0.0
    pb.interval_rain = 0.0
    pb.total_rain = 1.4
    pb.precipitation_type = 0.0
    pb.wind_direction = 63.0
    pb.wind_speed = 1.9
    pb.maximum_wind_speed = 2.8
    pb.barometric_pressure = 780.0
    pb.heading = 322.0
    pb.battery_life = 12.0
    pb.measurement_id = 15

    return pb.SerializeToString(), raw_size


@log_test_func
def test_iotpond1():
    from protobuf import iotpond1_pb2
    huffman = Huffman()

    json_string = """
    {
        "created_at":"2021-06-19 00:00:05 CET",
        "entry_id":1889,
        "Temperature (C)":24.875,
        "Turbidity(NTU)":100,
        "Dissolved Oxygen(g\/ml)":4.505,
        "PH":8.43365,
        "Ammonia(g\/ml)":0.45842,
        "Nitrate(g\/ml)":193,
        "Population":50,
        "Fish_Length(cm)":7.11,
        "Fish_Weight(g)":2.91
    }
    """
    raw_size = calculate_json_size(json_string)

    pb = iotpond1_pb2.Pond()
    pb.created_at = "2021-06-19 00:00:05 CET"
    pb.entry_id = 1889
    pb.temperature = 24.875
    pb.turbidity = 100
    pb.dissolved_oxygen = 4.505
    pb.ph = 8.43365
    pb.ammonia = 0.45842
    pb.nitrate = 193
    pb.population = 50
    pb.fish_length = 7.11
    pb.fish_weight = 2.91

    return pb.SerializeToString(), raw_size


@log_test_func
def test_iotpond1_normal():
    from protobuf import iotpond1_pb2
    huffman = Huffman()

    json_string = """
    {
        "created_at":"2021-06-19 00:00:05 CET",
        "entry_id":1889,
        "Temperature (C)":24.875,
        "Turbidity(NTU)":100,
        "Dissolved Oxygen(g\/ml)":4.505,
        "PH":8.43365,
        "Ammonia(g\/ml)":0.45842,
        "Nitrate(g\/ml)":193,
        "Population":50,
        "Fish_Length(cm)":7.11,
        "Fish_Weight(g)":2.91
    }
    """
    raw_size = calculate_json_size(json_string)

    pb = iotpond1_pb2.PondNormal()
    pb.created_at.FromSeconds(1624053605)
    pb.entry_id = 1889
    pb.temperature = 24.875
    pb.turbidity = 100
    pb.dissolved_oxygen = 4.505
    pb.ph = 8.43365
    pb.ammonia = 0.45842
    pb.nitrate = 193
    pb.population = 50
    pb.fish_length = 7.11
    pb.fish_weight = 2.91

    return pb.SerializeToString(), raw_size


@log_test_func
def test_iot_network_logs():
    from protobuf import iot_network_logs_pb2
    huffman = Huffman()

    json_string = """
    {
        "frame.number":1,
        "frame.time":123722736684743,
        "frame.len":54,
        "eth.src":87971959760497,
        "eth.dst":167275820076079,
        "ip.src":192168035,
        "ip.dst":1921680121,
        "ip.proto":6.0,
        "ip.len":40.0,
        "tcp.len":0.0,
        "tcp.srcport":49279.0,
        "tcp.dstport":80.0,
        "Value":-99.0,
        "normality":0
    }
    """
    raw_size = calculate_json_size(json_string)

    pb = iot_network_logs_pb2.NetworkLogs()
    pb.frame_number = 1
    pb.frame_time = 123722736684743
    pb.frame_len = 54
    pb.eth_src = 87971959760497
    pb.eth_dst = 167275820076079
    pb.ip_src = 192168035
    pb.ip_dst = 1921680121
    pb.ip_proto = 6.0
    pb.ip_len = 40.0
    pb.tcp_len = 40.0
    pb.tcp_srcport = 49279.0
    pb.tcp_dstport = 80.0
    pb.value = -99.0
    pb.normality = 0

    return pb.SerializeToString(), raw_size


@log_test_func
def test_all_sites_combined():
    from protobuf import all_sites_combined_pb2
    huffman = Huffman()

    json_string = """
    {
        "A NO2":2.706,
        "A UFP":11777.139,
        "A BC ":-0.0130518887
    }
    """
    raw_size = calculate_json_size(json_string)

    pb = all_sites_combined_pb2.ConcentrationGroup()
    pb.no2 = 2.706
    pb.ufp = 11777.139
    pb.bc = -0.0130518887

    return pb.SerializeToString(), raw_size


@log_test_func
def test_armourdale():
    from protobuf import armourdale_pb2
    huffman = Huffman()

    json_string = """
    {
        "Mo":10,
        "Dy":22,
        "Yr":17,
        "Z1UFP-NW":11777.139,
        "Z1BC-NW":-0.013051889,
        "Z1NO2-NW":2.706
    }
    """
    raw_size = calculate_json_size(json_string)

    pb = armourdale_pb2.ConcentrationGroupDate()
    pb.mo = -9999
    pb.dy = -9999
    pb.yr = -9999
    pb.no2 = 2.706
    pb.ufp = 11777.139
    pb.bc = -0.013051889

    return pb.SerializeToString(), raw_size


@log_test_func
def test_armourdale_normal():
    from protobuf import armourdale_pb2
    huffman = Huffman()

    json_string = """
    {
        "Mo":10,
        "Dy":22,
        "Yr":17,
        "Z1UFP-NW":11777.139,
        "Z1BC-NW":-0.013051889,
        "Z1NO2-NW":2.706
    }
    """
    raw_size = calculate_json_size(json_string)

    pb = armourdale_pb2.ConcentrationGroupDateNormal()
    pb.timestamp.FromSeconds(1715209533)
    pb.no2 = 2.706  # -2_147_483_648
    pb.ufp = 11777.139
    pb.bc = -0.013051889

    return pb.SerializeToString(), raw_size


huffman = Huffman()

test_iot_temp()
test_iot_temp_normal()

test_beach_water()
test_beach_water_normal()

test_beach_weather()
test_beach_weather_normal()

test_iotpond1()
test_iotpond1_normal()

test_iot_network_logs()

test_all_sites_combined()

test_armourdale()
test_armourdale_normal()
