from datetime import datetime

from data import iotj_pb2
from common.utils import load_yaml

from pathlib import Path
import random

from common.huffman import Huffman
from common.extended_huffman import calculate_size_in_bytes, calculate_compressed_size_in_bytes


pb = iotj_pb2.iotj()
pb.rxinfo.channel = 1
pb.rxinfo.codeRate = "4/5"
pb.rxinfo.crcStatus = 1
pb.rxinfo.dataRate.bandwidth = 125
pb.rxinfo.dataRate.modulation = iotj_pb2.rate.LORA
pb.rxinfo.dataRate.spreadFactor = 7
pb.rxinfo.frequency = 868300000
pb.rxinfo.loRaSNR = 7
pb.rxinfo.mac = "1dee08d0b691d149"
pb.rxinfo.rfChain = 1
pb.rxinfo.rssi = -57
pb.rxinfo.size = 23
pb.rxinfo.time.FromJsonString("2024-04-13T12:00:00Z")
pb.rxinfo.timestamp.FromSeconds(2074240683)

# yaml_path = 'data/message_pattern.yml'
# data = load_yaml(Path(yaml_path))

# Заполнение Protobuf из данных YAML

pb.phyPayload = str(random.uniform(-1999.9, 1999.9))

print(pb)

serialized_data = pb.SerializeToString()
print(serialized_data)

huffman = Huffman()

encoded_data, code_book = huffman.encode(serialized_data)
print("\nEncoded:", encoded_data)

decoded_data = huffman.decode(encoded_data, code_book)
print("\nDecoded:", decoded_data)

original_size = calculate_size_in_bytes(serialized_data)
compressed_size = calculate_compressed_size_in_bytes(encoded_data)

print("\nOriginal size:", original_size, "bytes")
print("Compressed size:", compressed_size, "bytes")
print("Compression ratio:", original_size / compressed_size)
print("Successful decode:", serialized_data == decoded_data)
