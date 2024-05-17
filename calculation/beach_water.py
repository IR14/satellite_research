from datetime import datetime
from typing import Tuple
import random

from common.utils import get_epoch, seconds_to_dateformat, get_json_size
from protobuf import beach_water_pb2

from . import ProtobufModule, ProtobufGeneratorModule


class BeachWaterModule(ProtobufModule):
    data_types = {
        'Measurement Timestamp': str,
        'Measurement Timestamp Label': str,

        'Beach Name': str,
        'Water Temperature': float,
        'Turbidity': float,
        'Transducer Depth': float,
        'Wave Height': float,
        'Wave Period': float,
        'Battery Life': float,
        'Measurement ID': str
    }

    beach_map = {
        'Montrose Beach': 'MONTROSE_BEACH',
        'Ohio Street Beach': 'OHIO_STREET_BEACH',
        'Calumet Beach': 'CALUMET_BEACH',
        '63rd Street Beach': 'STREET_BEACH_63RD',
        'Osterman Beach': 'OSTERMAN_BEACH',
        'Rainbow Beach': 'RAINBOW_BEACH'
    }

    @staticmethod
    def datetime_to_seconds(datetime_field: str) -> int:
        date_time_object = datetime.strptime(datetime_field, "%m/%d/%Y %I:%M:%S %p")
        epoch = get_epoch()
        seconds = int((date_time_object - epoch).total_seconds())
        return seconds

    @staticmethod
    def create_rational(
            beach_water_rational_fields: Tuple[int, str, float, float, float, float, float, float, str]
    ) -> beach_water_pb2.WaterMetricsRational:
        pb = beach_water_pb2.WaterMetricsRational()
        pb.timestamp.FromSeconds(beach_water_rational_fields[0])
        pb.timestamp_m.FromSeconds(beach_water_rational_fields[0])

        pb.beach = beach_water_rational_fields[1]
        pb.temperature = beach_water_rational_fields[2]
        pb.turbidity = beach_water_rational_fields[3]
        pb.transducer_depth = beach_water_rational_fields[4]
        pb.wave_height = beach_water_rational_fields[5]
        pb.wave_period = beach_water_rational_fields[6]
        pb.battery_life = beach_water_rational_fields[7]
        pb.id = beach_water_rational_fields[8]
        return pb

    def serialize_rational(self, row: dict) -> bytes:
        seconds = self.datetime_to_seconds(row['Measurement Timestamp'])
        data_tuple = (seconds,) + tuple(row[key] for key in list(self.data_types)[2:])
        pb = self.create_rational((data_tuple))
        return pb.SerializeToString()

    @staticmethod
    def create_normal(
            beach_water_rational_fields: Tuple[int, str, float, float, float, float, float, float]
    ) -> beach_water_pb2.WaterMetricsNormal:
        pb = beach_water_pb2.WaterMetricsNormal()
        pb.timestamp.FromSeconds(beach_water_rational_fields[0])
        pb.beach = beach_water_rational_fields[1]
        pb.temperature = beach_water_rational_fields[2]
        pb.turbidity = beach_water_rational_fields[3]
        pb.transducer_depth = beach_water_rational_fields[4]
        pb.wave_height = beach_water_rational_fields[5]
        pb.wave_period = beach_water_rational_fields[6]
        pb.battery_life = beach_water_rational_fields[7]
        return pb

    def serialize_normal(self, row: dict) -> bytes:
        seconds = self.datetime_to_seconds(row['Measurement Timestamp'])

        data_tuple = (seconds, self.beach_map[row['Beach Name']],) + tuple(row[key] for key in list(self.data_types)[3:])
        pb = self.create_rational((data_tuple))
        return pb.SerializeToString()


class BeachWaterGenerator(ProtobufGeneratorModule, BeachWaterModule):
    @staticmethod
    def get_formatted_date_time(seconds: int) -> str:
        formatted_date_time = seconds_to_dateformat(seconds, "%m/%d/%Y %I:%M:%S %p")
        return formatted_date_time

    @staticmethod
    def get_measurement_formatted_date_time(seconds: int) -> str:
        formatted_date_time = seconds_to_dateformat(seconds, "%-m/%-d/%Y %-I:%M %p")
        return formatted_date_time

    @staticmethod
    def get_measurement_id(beach_name: str, seconds: int) -> str:
        date_time = datetime.utcfromtimestamp(seconds)
        formatted_date_time = date_time.strftime("%Y%m%d")
        random_tick = random.randint(0, 24)
        random_measurement_id = ''.join(
            beach_name.split(' ') + [
                formatted_date_time,
                f"{random_tick:02}00"
            ]
        )
        return random_measurement_id

    def randomize_beach_name(self) -> (str, str):
        beach_choice = random.choice(
            list(self.beach_map.keys())
        )
        return beach_choice, self.beach_map[beach_choice]

    @staticmethod
    def randomize_temperature() -> float:
        return round(random.uniform(-10, 50), 3)

    @staticmethod
    def randomize_turbidity() -> float:
        return round(random.uniform(0, 5000), 3)

    @staticmethod
    def randomize_transducer_depth() -> float:
        return round(random.uniform(-10, 10), 3)

    @staticmethod
    def randomize_wave_height() -> float:
        return round(random.uniform(-10, 10), 3)

    @staticmethod
    def randomize_wave_period() -> float:
        return round(random.uniform(-50, 50), 3)

    @staticmethod
    def randomize_battery_life() -> float:
        return round(random.uniform(0, 100), 3)

    def randomize_attributes(self) -> Tuple[float, float, float, float, float, float]:
        random_attributes = (
            self.randomize_temperature(),
            self.randomize_turbidity(),
            self.randomize_transducer_depth(),
            self.randomize_wave_height(),
            self.randomize_wave_period(),
            self.randomize_battery_life()
        )
        return random_attributes

    def randomize_process(self, random_beach_key: str) -> Tuple[int, str, str, str, Tuple]:
        random_seconds = self.get_random_datetime_in_seconds()
        formatted_date_time = self.get_formatted_date_time(random_seconds)
        measurement_formatted_date_time = self.get_measurement_formatted_date_time(random_seconds)
        measurement_id = self.get_measurement_id(random_beach_key, random_seconds)
        random_attributes = self.randomize_attributes()
        return random_seconds, formatted_date_time, measurement_formatted_date_time, measurement_id, random_attributes

    def serialize_rational(self) -> (int, bytes):
        random_beach_key, _ = self.randomize_beach_name()

        random_seconds, formatted_date_time, measurement_formatted_date_time, measurement_id, random_attributes = self.randomize_process(
            random_beach_key)
        json_dict = self.fill_json_pattern((
            formatted_date_time, measurement_formatted_date_time, random_beach_key, *random_attributes, measurement_id
        ))
        pb = self.create_rational((
            random_seconds, random_beach_key, *random_attributes, measurement_id
        ))
        return get_json_size(json_dict), pb.SerializeToString()

    def serialize_normal(self) -> (int, bytes):
        random_beach_key, random_beach_value = self.randomize_beach_name()

        random_seconds, formatted_date_time, measurement_formatted_date_time, measurement_id, random_attributes = self.randomize_process(
            random_beach_key)

        json_dict = self.fill_json_pattern((
            formatted_date_time, measurement_formatted_date_time, random_beach_value, *random_attributes, measurement_id
        ))
        pb = self.create_normal((
            random_seconds, random_beach_value, *random_attributes
        ))
        return get_json_size(json_dict), pb.SerializeToString()
