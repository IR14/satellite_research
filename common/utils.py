import json
import yaml
import csv
from pathlib import Path
from common.model import JsonType
import random
from functools import wraps
from datetime import datetime


def timer_func(message_pattern):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_timestamp = datetime.now()
            result = func(*args, **kwargs)
            end_timestamp = datetime.now()
            print(f'{func.__name__}: {message_pattern.format(end_timestamp - start_timestamp)}')
            return result

        return wrapper

    return decorator


def get_epoch() -> datetime:
    epoch = datetime(1970, 1, 1)
    return epoch


def seconds_to_dateformat(seconds: int, date_pattern: str) -> str:
    date_time = datetime.utcfromtimestamp(seconds)
    formatted_date_time = date_time.strftime(date_pattern)
    return formatted_date_time


def randomize_id() -> int:
    return random.randint(0, 999_999)


def load_yaml(file_path: Path) -> JsonType:
    with file_path.open('r', encoding='ascii') as f:
        result = yaml.safe_load(f)
    return result


def load_json(file_path: Path) -> JsonType:
    with file_path.open('r', encoding='ascii') as f:
        result = json.load(f)
    return result


def get_json_size(json_data: dict) -> int:
    serialized_json_str = json.dumps(json_data, separators=(',', ':'))
    json_raw_size = len(serialized_json_str.encode('utf-8'))
    return json_raw_size


def read_csv(file_path: Path) -> JsonType:
    with file_path.open('r', encoding='utf-8') as f:
        reader = csv.reader(f)
        data = list(reader)
    return data
