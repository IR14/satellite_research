# #
# # Примерные данные для демонстрации
# data_samples = [
#     b"hello world",
#     b"hello there",
#     b"hello hello",
#     b"world hello",
#     b"test message",
#     b"message test"
# ]
#
# # Создание экземпляра класса HuffmanAdaptiveCodebook
# codebook = HuffmanAdaptiveCodebook(max_phrase_length=5)
#
# # Вычисление частот всех возможных фраз и построение дерева Хаффмана
# frequencies = codebook.calculate_all_phrase_frequencies(data_samples)
# root = codebook.build_huffman_tree(frequencies)
#
# # Генерация кодов Хаффмана для всех фраз
# codebook.generate_codes(root)
#
# # Кодирование сообщения
# original_message = b"world hello world"
# print(f'Original message: {original_message}')
# encoded_message = codebook.encode_data(original_message)
# print(f'Encoded message: {encoded_message}')
#
# print(f'Size of original message: {len(original_message)}')
# print(f'Size of encoded message: {(len(encoded_message) + 7) // 8}')
#
# # Декодирование сообщения
# decoded_message = codebook.decode_data(encoded_message)
#
# # Сериализация кодовой книги
# serialized_codebook = codebook.serialize_codebook()
# print(f'Size of serialized codebook: {len(serialized_codebook)}')
#
# # Десериализация кодовой книги
# new_codebook = HuffmanAdaptiveCodebook(max_phrase_length=5)
# new_codebook.deserialize_codebook(serialized_codebook)
#
# # Проверка, что раскодированное сообщение идентично оригинальному
# print("Original message:", original_message)
# print("Decoded message:", decoded_message)
# print("Messages are identical:", original_message == decoded_message)
#
# # Проверка, что кодовые книги идентичны
# print("Codebooks are identical:", codebook.huffman_codes == new_codebook.huffman_codes)
#
#
# def bitarray_to_bytes(bit_arr):
#     return bit_arr.tobytes()
#
#
# message_bytes = bitarray_to_bytes(encoded_message)
#
# print(message_bytes, len(message_bytes))
#
# from bitarray import bitarray
# import struct
#
# #
# def serialize_bitarray(bit_arr):
#     bit_length = len(bit_arr)
#     # Используем один байт для хранения длины
#     packed_data = struct.pack('>B', bit_length) + bit_arr.tobytes()
#     return packed_data
#
#
# def deserialize_bitarray(packed_data):
#     # Извлечение длины (1 байт)
#     bit_length = struct.unpack('>B', packed_data[:1])[0]
#     bit_arr = bitarray()
#     bit_arr.frombytes(packed_data[1:])
#     bit_arr = bit_arr[:bit_length]
#     return bit_arr
#
#
# # def serialize_bitarray(bit_arr):
# #     bit_length = len(bit_arr)
# #     # Используем два байта для хранения длины
# #     packed_data = struct.pack('>H', bit_length) + bit_arr.tobytes()
# #     return packed_data
# #
# #
# # def deserialize_bitarray(packed_data):
# #     # Извлечение длины (2 байта)
# #     bit_length = struct.unpack('>H', packed_data[:2])[0]
# #     bit_arr = bitarray()
# #     bit_arr.frombytes(packed_data[2:])
# #     bit_arr = bit_arr[:bit_length]
# #     return bit_arr
#
#
# # Предположим, что у вас есть bitarray, который вы хотите сериализовать
# example_bitarray = bitarray('01111101000011110001100111000')
#
# # Сериализация bitarray
# packed_data = serialize_bitarray(example_bitarray)
#
# # Предположим, эта байтовая строка передается, а затем десериализуется
# received_bitarray = deserialize_bitarray(packed_data)
#
# # Проверяем, что все корректно восстановлено
# print(f"Original bitarray: {example_bitarray}. LEN = {len(example_bitarray)} BIT")
# print("Received bitarray:", received_bitarray)
# print("Are they equal?", example_bitarray == received_bitarray)
# print(f'Deserialized message: {packed_data}, LEN: { len(packed_data)} BYTE')
# # print(example_bitarray, len(example_bitarray))
