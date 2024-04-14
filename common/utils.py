import json
import yaml
from pathlib import Path
from common.model import JsonType


def load_yaml(file_path: Path) -> JsonType:
    with file_path.open('r', encoding='ascii') as f:
        result = yaml.safe_load(f)

    return result


# def import_data_json(path):
#     if os.path.isfile(path):
#         with open(path, 'r') as read_file:
#             data_json = json.load(read_file)
#         return data_json
#     return None


def load_json(file_path: Path) -> JsonType:
    with file_path.open('r', encoding='ascii') as f:
        result = json.load(f)

    return result


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
