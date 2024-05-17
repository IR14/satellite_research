import argparse
from generate_codebook import positive_int, update_encoding_stats
import pathlib
from collections import defaultdict
from generate_codebook import load_codebook, deserialize_codebook, get_module_process

from calculation import ProtobufGeneratorModule
from calculation.iot_temp import IotTempGenerator
from calculation.beach_water import BeachWaterGenerator
from calculation.iot_pond import IotPondGenerator
from calculation.all_sites import AllSitesGenerator
from calculation.iot_network_logs import IotNetworkLogsGenerator


class ProtobufGeneratorModuleFactory:
    module_map = {
        "iot_temp": IotTempGenerator,
        "beach_water": BeachWaterGenerator,
        "iot_pond": IotPondGenerator,
        "all_sites": AllSitesGenerator,
        "network_logs": IotNetworkLogsGenerator,
    }

    @staticmethod
    def get_module(dataset_type: str) -> ProtobufGeneratorModule:
        if protobuf_module := ProtobufGeneratorModuleFactory.module_map.get(dataset_type):
            return protobuf_module()
        else:
            raise ValueError("Unknown Dataset Type")


def generate_messages(
        dataset_name: str,
        serialization_type: str,
        codebook_filename: pathlib.Path,
        phrase_length: int,
        messages_number: int
) -> None:
    _, serializator = get_module_process(
        ProtobufGeneratorModuleFactory, dataset_name, serialization_type
    )

    serialized_codebook = load_codebook(codebook_filename)
    codebook = deserialize_codebook(serialized_codebook, phrase_length)

    result = defaultdict(lambda: [0, 0, 0, -1, -1])
    for _ in range(messages_number):
        original_json_size, serialized_message = serializator()
        encoded_message = codebook.encode_data(serialized_message)
        serialized_size = len(serialized_message)
        encoded_size = (len(encoded_message) + 7) // 8
        update_encoding_stats(result, original_json_size, serialized_size, encoded_size)

    for key, value in result.items():
        print(f'{key}: {value}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run random message generation with configuration')
    parser.add_argument(
        '--dataset_name',
        '-d',
        type=str,
        required=True,
        choices=['iot_temp', 'beach_water', 'iot_pond', 'all_sites', 'network_logs'],
        help='Dataset name for huffman codebook loading'
    )
    parser.add_argument(
        '--serialization_type',
        '-s',
        type=str,
        required=True,
        choices=['rational', 'normal'],
        help='Type of dataset messages serialization'
    )
    parser.add_argument(
        '--codebook_filename',
        '-f',
        type=str,
        required=True,
        help='Huffman codebook filename to load'
    )
    parser.add_argument(
        '--phrase_length',
        '-p',
        type=positive_int,
        default=1,
        help='Max constraint for phrase length in huffman codebook'
    )
    parser.add_argument(
        '--number_of_messages',
        '-n',
        type=positive_int,
        default=1,
        help='Number of messages to generate'
    )

    args = parser.parse_args()
    dataset_name = args.dataset_name
    serialization_type = args.serialization_type
    codebook_filename = args.codebook_filename
    max_phrase_length = args.phrase_length
    messages_number = args.number_of_messages

    generate_messages(
        dataset_name=dataset_name,
        serialization_type=serialization_type,
        codebook_filename=pathlib.Path(codebook_filename),
        phrase_length=max_phrase_length,
        messages_number=messages_number
    )
