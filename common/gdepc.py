import huffman

from typing import Union


class DataProcessor:
    def __init__(self, protobuf_obj):
        self.data = protobuf_obj

    def serialize(self):
        return self.data.SerializeToString()

    def split_into_sbd_messages(self, max_size=340):
        serialized_data = self.serialize()
        messages = []
        for i in range(0, len(serialized_data), max_size):
            messages.append(serialized_data[i:i + max_size])
        return messages


class GDEPC:
    def __init__(self, data):
        self.data = data

    # @staticmethod
    # def serialize_to_bytes(data):
    #     json_data = json.dumps(data)
    #     return json_data.encode('utf-8')

    @staticmethod
    def compress_data_huffman(data):
        encoded_data, tree = huffman.huffman_encode(data)
        return encoded_data, tree

    @staticmethod
    def repackage_into_containers(data_messages: Union[list, bytearray], max_size=340):
        if not isinstance(data_messages, list):
            data_messages = [data_messages]
        containers = []
        current_container = bytearray()

        for message in data_messages:
            for byte in message:
                current_container.append(byte)
                if len(current_container) == max_size:
                    containers.append(current_container)
                    current_container = bytearray()

        if current_container:
            containers.append(current_container)

        return containers

    def process_and_repackage(self, data_blocks):
        compressed_blocks = []

        for block in data_blocks:
            compressed, _ = self.compress_data_huffman(block)
            compressed_blocks.append(compressed)

        new_containers = self.repackage_into_containers(compressed_blocks)

        return new_containers
