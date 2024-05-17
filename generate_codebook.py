import pandas as pd
from collections import defaultdict

import argparse
import pathlib

from common.huffman_adaptive_codebook import HuffmanAdaptiveCodebook
from common.utils import timer_func

from typing import List, Callable, Optional

from concurrent.futures import ProcessPoolExecutor

from calculation import ProtobufModule
from calculation.iot_temp import IotTempModule
from calculation.beach_water import BeachWaterModule
from calculation.iot_pond import IotPondModule
from calculation.all_sites import AllSitesModule
from calculation.iot_network_logs import IotNetworkLogsModule


class ProtobufModuleFactory:
    module_map = {
        "iot_temp": IotTempModule,
        "beach_water": BeachWaterModule,
        "iot_pond": IotPondModule,
        "all_sites": AllSitesModule,
        "network_logs": IotNetworkLogsModule,
    }

    @staticmethod
    def get_module(dataset_type: str) -> ProtobufModule:
        if protobuf_module := ProtobufModuleFactory.module_map.get(dataset_type):
            return protobuf_module()
        else:
            raise ValueError("Unknown Dataset Type")


@timer_func('CODEBOOK SAVED ({} sec)')
def save_codebook(serialized_codebook: bytes, filename: pathlib.Path) -> None:
    with open(filename, 'wb') as f:
        f.write(serialized_codebook)


@timer_func('CODEBOOK LOADED ({} sec)')
def load_codebook(filename: pathlib.Path) -> bytes:
    with open(filename, 'rb') as f:
        serialized_codebook = f.read()
    return serialized_codebook


@timer_func('CODEBOOK SERIALIZED ({} sec)')
def serialize_codebook(codebook: HuffmanAdaptiveCodebook) -> bytes:
    serialized_codebook = codebook.serialize_codebook()
    return serialized_codebook


@timer_func('CODEBOOK INITIALIZED AND DESERIALIZED ({} sec)')
def deserialize_codebook(serialized_codebook: bytes, phrase_length: int) -> HuffmanAdaptiveCodebook:
    codebook = HuffmanAdaptiveCodebook(max_phrase_length=phrase_length)
    codebook.deserialize_codebook(serialized_codebook)
    return codebook


@timer_func('CODEBOOK GENERATED ({} sec)')
def generate_codebook(data: List[bytes], phrase_length: int) -> HuffmanAdaptiveCodebook:
    codebook = HuffmanAdaptiveCodebook(max_phrase_length=phrase_length)
    frequencies = codebook.calculate_all_phrase_frequencies(data)
    root = codebook.build_huffman_tree(frequencies)
    codebook.generate_codes(root)
    return codebook


def process_data_sample(data: bytes, codebook) -> dict:
    try:
        encoded = codebook.encode_data(data)
        decoded = codebook.decode_data(encoded)
        is_correct = data == decoded

        original_size = len(data)
        encoded_size = (len(encoded) + 7) // 8

        return {
            'original_size': original_size,
            'encoded_size': encoded_size,
            'is_correct': is_correct
        }

    except Exception as e:
        return {
            'error': str(e),
            'original_size': len(data),
            'encoded_size': None,
            'is_correct': False
        }


def compare_huffman_codes(huffman_codes: dict, other_huffman_codes: dict) -> bool:
    compare_flag = huffman_codes == other_huffman_codes
    print("CODEBOOKS ARE IDENTICAL:", compare_flag)
    return compare_flag


@timer_func('DATASET MESSAGES SERIALIZED ({} sec)')
def serialize_data(df: pd.DataFrame, serializator: Callable[[], bytes]) -> List[bytes]:
    with ProcessPoolExecutor() as executor:
        data = list(
            executor.map(
                serializator,
                [dict(row) for _, row in df.iterrows()]
            )
        )
    return data


def update_encoding_stats(encoding_maps, original_size, serialized_size, encoded_size):
    encoding_maps[serialized_size][0] += original_size
    encoding_maps[serialized_size][1] += encoded_size
    encoding_maps[serialized_size][2] += 1

    if encoding_maps[serialized_size][3] == -1:
        encoding_maps[serialized_size][3] = encoded_size
    else:
        encoding_maps[serialized_size][3] = min(encoding_maps[serialized_size][3], encoded_size)

    encoding_maps[serialized_size][4] = max(encoding_maps[serialized_size][4], encoded_size)


def load_process(filename: pathlib.Path, phrase_length: int) -> HuffmanAdaptiveCodebook:
    serialized_codebook = load_codebook(filename)
    codebook = deserialize_codebook(serialized_codebook, phrase_length)
    return codebook


def generation_process(filename: pathlib.Path, data: List[bytes], phrase_length: int) -> HuffmanAdaptiveCodebook:
    generated_codebook = generate_codebook(data, phrase_length)
    serialized_codebook = serialize_codebook(generated_codebook)
    save_codebook(serialized_codebook, filename)
    return generated_codebook


@timer_func('MESSAGES FROM DATASET ENCODED ({} sec)')
def encode_dataset_messages(data: List[bytes], data_num: int, codebook: HuffmanAdaptiveCodebook) -> None:
    encoding_maps = defaultdict(lambda: [0, 0, 0, -1, -1])

    results = []
    for message in data[:data_num]:
        results.append(process_data_sample(message, codebook))

    for metric in results:
        if 'error' in metric:
            continue
        if not metric['is_correct']:
            continue
        update_encoding_stats(encoding_maps, metric['original_size'], metric['encoded_size'])

    for key, value in encoding_maps.items():
        print(f'"{key}": {value},')


def get_module_process(factory, dataset_name: str, serialization_type: str):
    protobuf_module = factory.get_module(dataset_name)
    serialization_type_map = {
        'raw': protobuf_module.serialize_raw,
        'rational': protobuf_module.serialize_rational,
        'normal': protobuf_module.serialize_normal,
    }
    serializator = serialization_type_map[serialization_type]
    return protobuf_module, serializator


def prepare_iot_temp(
        dataset_name: str,
        serialization_type: str,
        codebook_process_type: str,
        dataset_filename: pathlib.Path,
        huffman_codebook_filename: pathlib.Path,
        phrase_length: int,
        dataset_encode_flag: Optional[bool] = None,
) -> None:
    protobuf_module, serializator = get_module_process(
        ProtobufModuleFactory, dataset_name, serialization_type
    )

    df = protobuf_module.prepare_df(dataset_filename)
    data = serialize_data(df, serializator)

    process_map = {
        'generate': (
            generation_process,
            {
                "filename": huffman_codebook_filename,
                "data": data,
                "phrase_length": phrase_length
            }
        ),
        'load': (
            load_process,
            {
                "filename": huffman_codebook_filename,
                "phrase_length": phrase_length
            }
        )
    }
    process_func = process_map[codebook_process_type][0]
    process_args = process_map[codebook_process_type][1]

    codebook = process_func(**process_args)

    if dataset_encode_flag:
        encode_dataset_messages(data, dataset_encode_flag, codebook)


def positive_int(value):
    value = int(value)
    if value < 1:
        raise argparse.ArgumentTypeError("Number should be greater than 0")
    return value


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run services with configuration')
    parser.add_argument(
        '--dataset_name',
        '-d',
        type=str,
        required=True,
        choices=['iot_temp', 'beach_water', 'iot_pond', 'all_sites', 'network_logs'],
        help='Dataset name for huffman codebook generation'
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
        '--phrase_length',
        '-p',
        type=positive_int,
        default=1,
        help='Max constraint for phrase length in huffman codebook'
    )

    args = parser.parse_args()
    dataset_name = args.dataset_name
    serialization_type = args.serialization_type
    max_phrase_length = args.phrase_length

    dataset_map = {
        'iot_temp': 'iot_temp.csv',
        'beach_water': 'beach_water_quality_automated_sensors_1.csv',
        'iot_pond': 'iotpond1.csv',
        'all_sites': 'all_sites.csv',
        'network_logs': 'iot_network_logs.csv',
    }

    dataset_dir = pathlib.Path('datasets')
    dataset_filename = dataset_dir / dataset_map[dataset_name]

    codebook_process_type = 'generate'
    dataset_encode_num = None
    codebook_filename = f'huffman_codebook_{dataset_name}_{serialization_type}_{max_phrase_length}.bin'

    prepare_iot_temp(
        dataset_name=dataset_name,
        serialization_type=serialization_type,
        codebook_process_type=codebook_process_type,
        dataset_filename=dataset_filename,
        huffman_codebook_filename=pathlib.Path(codebook_filename),
        phrase_length=max_phrase_length,
    )
