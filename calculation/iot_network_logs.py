from datetime import datetime
from typing import Tuple
import random
import pandas as pd
import pathlib

from common.utils import seconds_to_dateformat, get_json_size, timer_func
from protobuf import iot_network_logs_pb2

from . import ProtobufModule, ProtobufGeneratorModule


class IotNetworkLogsModule(ProtobufModule):
    data_types = {
        "frame.number": int,
        "frame.time": int,
        "frame.len": int,
        "eth.src": int,
        "eth.dst": int,
        "ip.src": int,
        "ip.dst": int,
        "ip.proto": float,
        "ip.len": float,
        "tcp.len": float,
        "tcp.srcport": float,
        "tcp.dstport": float,
        "Value": float,
        "normality": int
    }

    @timer_func('DF VALIDATION COMPLETED ({} sec)')
    def prepare_df(self, filename: pathlib.Path) -> pd.DataFrame:
        df = pd.read_csv(filename)
        df = df.astype(self.data_types)
        df.dropna(inplace=True)
        df['ip.src'] = df['ip.src'].astype(int)
        df['ip.dst'] = df['ip.dst'].astype(int)
        df['normality'] = df['normality'].astype(int)
        return df

    @staticmethod
    def create_rational(
            iot_network_logs_rational_fields: Tuple[
                int, int, int, int, int, int, int, float, float, float, float, float, float, int
            ]
    ) -> iot_network_logs_pb2.NetworkLogs:
        pb = iot_network_logs_pb2.NetworkLogs()
        pb.frame_number = int(iot_network_logs_rational_fields[0])
        pb.frame_time = int(iot_network_logs_rational_fields[1])
        pb.frame_len = int(iot_network_logs_rational_fields[2])
        pb.eth_src = int(iot_network_logs_rational_fields[3])
        pb.eth_dst = int(iot_network_logs_rational_fields[4])
        pb.ip_src = int(iot_network_logs_rational_fields[5])
        pb.ip_dst = int(iot_network_logs_rational_fields[6])
        pb.ip_proto = float(iot_network_logs_rational_fields[7])
        pb.ip_len = float(iot_network_logs_rational_fields[8])
        pb.tcp_len = float(iot_network_logs_rational_fields[9])
        pb.tcp_srcport = float(iot_network_logs_rational_fields[10])
        pb.tcp_dstport = float(iot_network_logs_rational_fields[11])
        pb.value = float(iot_network_logs_rational_fields[12])
        pb.normality = int(iot_network_logs_rational_fields[13])
        return pb

    def serialize_rational(self, row: dict) -> bytes:
        pb = self.create_rational((
            tuple(row[key] for key in self.data_types)
        ))
        return pb.SerializeToString()


class IotNetworkLogsGenerator(ProtobufGeneratorModule, IotNetworkLogsModule):
    @staticmethod
    def randomize_frame_time() -> int:
        return random.randint(100_000_000_000_000, 200_000_000_000_000)

    @staticmethod
    def randomize_frame_len() -> int:
        return random.randint(0, 5_000)

    @staticmethod
    def randomize_eth_src_dst() -> int:
        return random.randint(0, 300_000_000_000_000)

    @staticmethod
    def randomize_ip_src_dst() -> int:
        return random.randint(0, 255_255_255_255)

    @staticmethod
    def randomize_ip_proto() -> float:
        return round(random.uniform(-20, 20), 1)

    @staticmethod
    def randomize_ip_tcp_len() -> float:
        return round(random.uniform(0, 5_000), 14)

    @staticmethod
    def randomize_tcp_src_dst() -> int:
        return random.randint(0, 65534)

    @staticmethod
    def randomize_value() -> int:
        return random.randint(-100, 5_000_000)

    @staticmethod
    def randomize_normality() -> int:
        return random.randint(0, 100)

    def randomize_attributes(self) -> Tuple:
        random_attributes = (
            self.randomize_int32_id(),
            self.randomize_frame_time(),
            self.randomize_frame_len(),
            self.randomize_eth_src_dst(),
            self.randomize_eth_src_dst(),
            self.randomize_ip_src_dst(),
            self.randomize_ip_src_dst(),
            self.randomize_ip_proto(),
            self.randomize_ip_tcp_len(),
            self.randomize_ip_tcp_len(),
            self.randomize_tcp_src_dst(),
            self.randomize_tcp_src_dst(),
            self.randomize_value(),
            self.randomize_normality()
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
