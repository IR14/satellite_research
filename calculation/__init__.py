from abc import ABC, abstractmethod
from typing import Tuple
import random
from datetime import datetime, timedelta
import pathlib
import pandas as pd
from common.utils import timer_func


class ProtobufModule(ABC):
    data_types = dict()

    @timer_func('DF VALIDATION COMPLETED ({} sec)')
    def prepare_df(self, filename: pathlib.Path) -> pd.DataFrame:
        df = pd.read_csv(filename)
        df = df.astype(self.data_types)
        df.dropna(inplace=True)
        return df

    def datetime_to_seconds(self, *args, **kwargs):
        pass

    def create_raw(self, *args, **kwarg):
        pass

    def serialize_raw(self, *args, **kwarg):
        pass

    @abstractmethod
    def create_rational(self, *args, **kwarg):
        pass

    @abstractmethod
    def serialize_rational(self, *args, **kwarg):
        pass

    def create_normal(self, *args, **kwarg):
        pass

    def serialize_normal(self, *args, **kwarg):
        pass


class ProtobufGeneratorModule(ABC):
    def seconds_to_datetime(self, *args, **kwarg):
        pass

    def serialize_raw(self, *args, **kwarg):
        pass

    @abstractmethod
    def serialize_rational(self, *args, **kwarg):
        pass

    def serialize_normal(self, *args, **kwarg):
        pass

    @staticmethod
    def randomize_int32_id() -> int:
        return random.randint(0, 999_999)

    @staticmethod
    def get_random_datetime_in_seconds(start_str: str = '01/01/2020', end_str: str = '31/12/2030') -> int:
        start_date = datetime.strptime(start_str, '%d/%m/%Y')
        end_date = datetime.strptime(end_str, '%d/%m/%Y')

        delta = end_date - start_date
        random_days = random.randint(0, delta.days)
        random_hours = random.randint(0, 23)
        random_minutes = random.randint(0, 59)

        random_date_time = start_date + timedelta(days=random_days, hours=random_hours, minutes=random_minutes)
        epoch = datetime(1970, 1, 1)
        random_date_seconds = int((random_date_time - epoch).total_seconds())
        return random_date_seconds

    def fill_json_pattern(self, fill_data: Tuple) -> dict:
        return {key: value for key, value in zip(self.data_types.keys(), fill_data)}
