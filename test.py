from protobuf import iotj_pb2, iot_temp_pb2

from common.huffman import Huffman

import deflate

# pb = iotj_pb2.iotj()
# pb.rxinfo.channel = 1
# pb.rxinfo.codeRate = "4/5"
# pb.rxinfo.crcStatus = 1
# pb.rxinfo.dataRate.bandwidth = 125
# pb.rxinfo.dataRate.modulation = iotj_pb2.rate.LORA
# pb.rxinfo.dataRate.spreadFactor = 7
# pb.rxinfo.frequency = 868300000
# pb.rxinfo.loRaSNR = 7
# pb.rxinfo.mac = "1dee08d0b691d149"
# pb.rxinfo.rfChain = 1
# pb.rxinfo.rssi = -57
# pb.rxinfo.size = 23
# pb.rxinfo.time.FromJsonString("2024-04-13T12:00:00Z")
# pb.rxinfo.timestamp.FromSeconds(2074240683)

pb = iot_temp_pb2.LogEntry()
pb.entity = "__export__.temp_log_196134_bd201015"
pb.user = "Room Admin"
pb.temperature = 29
pb.timestamp.FromSeconds(2074240683)
pb.status = "In"

# a = {
#     1: "__export__.temp_log_196134_bd201015",
#     2: "Room Admin",
#     3: "08-12-2018 09:30",
#     4: 29,
#     5: "In"
# }
# print()
# yaml_path = 'data/message_pattern.yml'
# data = load_yaml(Path(yaml_path))

# Заполнение Protobuf из данных YAML

# pb.phyPayload = str("this is an example of a huffman tree with extended dictionary capabilities.")

print(pb)

serialized_data = pb.SerializeToString()
print(serialized_data)

huffman = Huffman()

encoded_data, code_book = huffman.encode(serialized_data)
print("\nEncoded:", encoded_data)

decoded_data = huffman.decode(encoded_data, code_book)
print("\nDecoded:", decoded_data)

# original_size = calculate_size_in_bytes(serialized_data)
# compressed_size = calculate_compressed_size_in_bytes(encoded_data)
# Размер исходных данных и сжатых данных
# original_size = len(serialized_data)
original_size = 96
compressed_size = (len(encoded_data) + 7) // 8

# Коэффициент сжатия
compression_ratio = original_size / compressed_size

print("\nOriginal size:", original_size, "bytes")
print("Compressed size:", compressed_size, "bytes")
print("Compression ratio:", original_size / compressed_size)
print("Successful decode:", serialized_data == decoded_data)

# Сериализованные данные
# serialized_data = b'your_serialized_data_here'

# # Сжатие данных с помощью Brotli
# compressed_data = brotli.compress(serialized_data)
# print(serialized_data)
#
# # Размер исходных данных и сжатых данных
# original_size = len(serialized_data)
# compressed_size = len(compressed_data)
#
# # Коэффициент сжатия
# compression_ratio = original_size / compressed_size
#
# # Вывод результатов
# print(f"Original size: {original_size} bytes")
# print(f"Compressed size: {compressed_size} bytes")
# print(f"Compression ratio: {compression_ratio}")

# level = 1  # The default; may be 1-12 for libdeflate.
# compressed = deflate.gzip_compress(serialized_data * 1000, level)
# original = deflate.gzip_decompress(compressed)

# # Размер исходных данных и сжатых данных
# original_size = len(serialized_data)
# compressed_size = len(compressed)
#
# # Коэффициент сжатия
# compression_ratio = original_size / compressed_size
#
# # Вывод результатов
# print(f"Original size: {original_size} bytes")
# print(f"Compressed size: {compressed_size} bytes")
# print(f"Compression ratio: {compression_ratio}")

# level = 6  # The default; may be 1-12 for libdeflate.
# ser = b"hello world!" * 1000
# ser = serialized_data
# ser = b"this is an example of a huffman tree with extended dictionary capabilities."
# print(ser)
# compressed = deflate.deflate_compress(ser, level)
# original = deflate.deflate_decompress(compressed, len(ser))
#
# Размер исходных данных и сжатых данных
# original_size = len(ser)
# compressed_size = len(compressed)
#
# Коэффициент сжатия
# compression_ratio = original_size / compressed_size
#
# Вывод результатов
# print(f"Original size: {original_size} bytes")
# print(f"Compressed size: {compressed_size} bytes")
# print(f"Compression ratio: {compression_ratio}")
