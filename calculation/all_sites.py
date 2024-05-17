from typing import Tuple
import random

from common.utils import get_json_size
from protobuf import all_sites_combined_pb2

from . import ProtobufModule, ProtobufGeneratorModule


class AllSitesModule(ProtobufModule):
    data_types = {
        'UFP': float,
        'BC': float,
        'NO2': float,
    }

    @staticmethod
    def create_rational(
            all_sites_rational_fields: Tuple[float, float, float]
    ) -> all_sites_combined_pb2.ConcentrationGroup:
        pb = all_sites_combined_pb2.ConcentrationGroup()
        pb.ufp = all_sites_rational_fields[0]
        pb.bc = all_sites_rational_fields[1]
        pb.no2 = all_sites_rational_fields[2]
        return pb

    def serialize_rational(self, row: dict) -> bytes:
        pb = self.create_rational((
            tuple(row[key] for key in self.data_types)
        ))
        return pb.SerializeToString()


class AllSitesGenerator(ProtobufGeneratorModule, AllSitesModule):
    @staticmethod
    def randomize_ufp() -> float:
        return round(random.uniform(0, 9_000_000), 3)

    @staticmethod
    def randomize_bc() -> float:
        return round(random.uniform(0, 2_000), 3)

    @staticmethod
    def randomize_no2() -> float:
        return round(random.uniform(0, 2_000), 3)

    def randomize_attributes(self) -> Tuple[float, float, float]:
        random_attributes = (
            self.randomize_ufp(),
            self.randomize_bc(),
            self.randomize_no2()
        )
        return random_attributes

    def serialize_rational(self) -> (int, bytes):
        random_attributes = self.randomize_attributes()
        json_dict = self.fill_json_pattern((
            random_attributes
        ))
        pb = self.create_rational((
            random_attributes
        ))
        return get_json_size(json_dict), pb.SerializeToString()
