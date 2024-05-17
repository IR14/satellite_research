import pathlib
import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple
import random

from common.utils import timer_func, get_epoch, seconds_to_dateformat, get_json_size
from protobuf import iot_pond_pb2

from . import ProtobufModule, ProtobufGeneratorModule


class IotPondModule(ProtobufModule):
    data_types = {
        'created_at': str,

        'entry_id': int,
        'Temperature (C)': float,
        'Turbidity(NTU)': int,
        'Dissolved Oxygen(g/ml)': float,
        'PH': float,
        'Ammonia(g/ml)': float,
        'Nitrate(g/ml)': int,
        'Population': int,
        'Fish_Length(cm)': float,
        'Fish_Weight(g)': float
    }

    @staticmethod
    def datetime_to_seconds(datetime_field: str) -> int:
        format_str = '%Y-%m-%d %H:%M:%S'
        datetime_part, _ = datetime_field.rsplit(' ', 1)
        naive_datetime = datetime.strptime(datetime_part, format_str)
        utc_datetime = naive_datetime - timedelta(hours=1)
        epoch = get_epoch()
        seconds = int((utc_datetime - epoch).total_seconds())
        return seconds

    @staticmethod
    def create_rational(
            iot_pond_rational_fields: Tuple[int, int, float, int, float, float, float, int, int, float, float]
    ) -> iot_pond_pb2.PondRational():
        pb = iot_pond_pb2.PondRational()
        pb.created_at.FromSeconds(iot_pond_rational_fields[0])
        pb.entry_id = iot_pond_rational_fields[1]
        pb.temperature = iot_pond_rational_fields[2]
        pb.turbidity = iot_pond_rational_fields[3]
        pb.dissolved_oxygen = iot_pond_rational_fields[4]
        pb.ph = iot_pond_rational_fields[5]
        pb.ammonia = iot_pond_rational_fields[6]
        pb.nitrate = iot_pond_rational_fields[7]
        pb.population = iot_pond_rational_fields[8]
        pb.fish_length = iot_pond_rational_fields[9]
        pb.fish_weight = iot_pond_rational_fields[10]
        return pb

    def serialize_rational(self, row: dict) -> bytes:
        seconds = self.datetime_to_seconds(row['created_at'])
        data_tuple = (seconds,) + tuple(row[key] for key in list(self.data_types)[1:])
        pb = self.create_rational(data_tuple)
        return pb.SerializeToString()


class IotPondGenerator(ProtobufGeneratorModule, IotPondModule):
    @staticmethod
    def seconds_to_datetime(seconds: int) -> str:
        formatted_date_time = seconds_to_dateformat(seconds, "%Y-%m-%d %H:%M:%S")
        return "".join([
            formatted_date_time, "CET"
        ])

    def fill_json_pattern(self, fill_data: Tuple) -> dict:
        return {key: value for key, value in zip(self.data_types.keys(), fill_data)}

    @staticmethod
    def randomize_temperature() -> float:
        return round(random.uniform(-200, 200), 4)

    @staticmethod
    def randomize_turbidity() -> int:
        return random.randint(0, 1000)

    @staticmethod
    def randomize_dissolved_oxygen() -> float:
        return round(random.uniform(0, 100), 3)

    @staticmethod
    def randomize_ph() -> float:
        return round(random.uniform(-1, 20), 5)

    @staticmethod
    def randomize_ammonia() -> float:
        return round(random.uniform(0, 999_000_000_000), 5)

    @staticmethod
    def randomize_nitrate() -> int:
        return random.randint(0, 9_000)

    @staticmethod
    def randomize_population() -> int:
        return random.randint(0, 100)

    @staticmethod
    def randomize_fish_length() -> float:
        return round(random.uniform(0, 100), 3)

    @staticmethod
    def randomize_fish_weight() -> float:
        return round(random.uniform(0, 1_000), 3)

    def randomize_attributes(self) -> Tuple[int, float, int, float, float, float, int, int, float, float]:
        random_attributes = (
            self.randomize_int32_id(),
            self.randomize_temperature(),
            self.randomize_turbidity(),
            self.randomize_dissolved_oxygen(),
            self.randomize_ph(),
            self.randomize_ammonia(),
            self.randomize_nitrate(),
            self.randomize_population(),
            self.randomize_fish_length(),
            self.randomize_fish_weight()
        )
        return random_attributes

    def serialize_rational(self) -> (int, bytes):
        random_seconds = self.get_random_datetime_in_seconds()
        random_attributes = self.randomize_attributes()
        formatted_date_time = self.seconds_to_datetime(random_seconds)

        json_dict = self.fill_json_pattern((formatted_date_time, *random_attributes))
        pb = self.create_rational((random_seconds, *random_attributes))
        return get_json_size(json_dict), pb.SerializeToString()
