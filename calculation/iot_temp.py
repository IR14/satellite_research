from datetime import datetime
from typing import Tuple
import re
import random
import string

from common.utils import timer_func, get_epoch, seconds_to_dateformat, get_json_size
from protobuf import iot_temp_pb2

from . import ProtobufModule, ProtobufGeneratorModule


class IotTempModule(ProtobufModule):
    data_types = {
        'id': str,
        'room_id/id': str,
        'noted_date': str,
        'temp': int,
        'out/in': str
    }

    @staticmethod
    def datetime_to_seconds(datetime_field: str) -> int:
        date_time_object = datetime.strptime(datetime_field, '%d-%m-%Y %H:%M')
        epoch = get_epoch()
        seconds = int((date_time_object - epoch).total_seconds())
        return seconds

    @staticmethod
    def create_raw(iot_temp_raw_fields: Tuple[str, str, str, int, str]) -> iot_temp_pb2.LogEntry:
        pb = iot_temp_pb2.LogEntry()
        pb.entity = iot_temp_raw_fields[0]
        pb.user = iot_temp_raw_fields[1]
        pb.timestamp = iot_temp_raw_fields[2]
        pb.temperature = iot_temp_raw_fields[3]
        pb.status = iot_temp_raw_fields[4]
        return pb

    def serialize_raw(self, row: dict) -> bytes:
        data_tuple = tuple(row[key] for key in self.data_types)
        pb = self.create_raw(data_tuple)
        return pb.SerializeToString()

    @staticmethod
    def create_rational(iot_temp_rational_fields: Tuple[str, str, int, int, str]) -> iot_temp_pb2.LogEntryRational:
        pb = iot_temp_pb2.LogEntryRational()
        pb.entity = iot_temp_rational_fields[0]
        pb.user = iot_temp_rational_fields[1]
        pb.timestamp.FromSeconds(iot_temp_rational_fields[2])
        pb.temperature = iot_temp_rational_fields[3]
        pb.status = iot_temp_rational_fields[4]
        return pb

    def serialize_rational(self, row: dict) -> bytes:
        seconds = self.datetime_to_seconds(row['noted_date'])
        pb = self.create_rational((
            row['id'],
            row['room_id/id'],
            seconds,
            row['temp'],
            row['out/in']
        ))
        return pb.SerializeToString()

    @staticmethod
    def create_normal(
            iot_temp_normal_fields: Tuple[str, int, int, str, int, int, str]
    ) -> iot_temp_pb2.LogEntryNormal:
        pb = iot_temp_pb2.LogEntryNormal()
        pb.messageSource = iot_temp_normal_fields[0]
        pb.tickHash = iot_temp_normal_fields[1]
        pb.messageHash = iot_temp_normal_fields[2]
        pb.user = iot_temp_normal_fields[3]
        pb.timestamp.FromSeconds(iot_temp_normal_fields[4])
        pb.temperature = iot_temp_normal_fields[5]
        pb.status = iot_temp_normal_fields[6]
        return pb

    def serialize_normal(self, row: dict) -> bytes:
        message_source_map = {
            "__export__.temp_log_": "TEMP_LOG"
        }
        user_map = {
            "Room Admin": "ROOM_ADMIN"
        }

        seconds = self.datetime_to_seconds(row['noted_date'])

        tick_hash = int(
            re.search(r'(\d+)_\w+', row['id']).group(1)
        )
        message_hash = int(
            re.search(r'_([0-9a-fA-F]+)$', row['id']).group(1),
            16
        )

        pb = self.create_normal((
            message_source_map[row['id'][:20]],
            tick_hash,
            message_hash,
            user_map[row['room_id/id']],
            seconds,
            row['temp'],
            row['out/in']
        ))
        return pb.SerializeToString()


class IotTempGenerator(ProtobufGeneratorModule, IotTempModule):
    @staticmethod
    def randomize_temperature() -> int:
        return random.randint(0, 99)

    @staticmethod
    def randomize_hex_with_length(length: int = 8) -> str:
        hex_characters = string.hexdigits[:-6]
        random_hex = ''.join(random.choice(hex_characters) for _ in range(length))
        return random_hex

    @staticmethod
    def randomize_status() -> str:
        return random.choice(["In", "Out"])

    def randomize_attributes(self) -> Tuple[dict, str, int, int, str, int, str]:
        random_id = self.randomize_int32_id()
        random_hex = self.randomize_hex_with_length()
        random_seconds = self.get_random_datetime_in_seconds()
        random_temp = self.randomize_temperature()
        random_status = self.randomize_status()

        formatted_date_time = seconds_to_dateformat(random_seconds, "%d-%m-%Y %H:%M")

        entity = ''.join([
            '__export__.temp_log_',
            str(random_id),
            random_hex
        ])

        json_dict = self.fill_json_pattern((
            entity,
            "Room Admin",
            formatted_date_time,
            random_temp,
            random_status
        ))
        return json_dict, entity, random_seconds, random_temp, random_status, random_id, random_hex

    def serialize_rational(self) -> (int, bytes):
        json_dict, entity, random_seconds, random_temp, random_status, _, _ = self.randomize_attributes()
        pb = self.create_rational((
            entity,
            "Room Admin",
            random_seconds,
            random_temp,
            random_status
        ))
        return get_json_size(json_dict), pb.SerializeToString()

    def serialize_normal(self) -> (int, bytes):
        message_source_map = {
            "__export__.temp_log_": "TEMP_LOG"
        }
        user_map = {
            "Room Admin": "ROOM_ADMIN"
        }

        json_dict, entity, random_seconds, random_temp, random_status, random_id, random_hex = self.randomize_attributes()

        pb = self.create_normal((
            message_source_map["__export__.temp_log_"],
            random_id,
            int(random_hex, 16),
            user_map["Room Admin"],
            random_seconds,
            random_temp,
            random_status
        ))
        return get_json_size(json_dict), pb.SerializeToString()
