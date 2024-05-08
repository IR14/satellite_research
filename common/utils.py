import json
import yaml
import csv
from pathlib import Path
from common.model import JsonType


def load_yaml(file_path: Path) -> JsonType:
    with file_path.open('r', encoding='ascii') as f:
        result = yaml.safe_load(f)

    return result


def load_json(file_path: Path) -> JsonType:
    with file_path.open('r', encoding='ascii') as f:
        result = json.load(f)

    return result


def read_csv(file_path: Path) -> JsonType:
    with file_path.open('r', encoding='utf-8') as f:
        reader = csv.reader(f)
        data = list(reader)

    return data
