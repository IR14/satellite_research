import heapq
from collections import defaultdict, Counter


class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq


class Huffman:
    def __init__(self, min_freq=0):
        self.root = None
        self.code_book = defaultdict(str)
        self.min_freq = min_freq

    @staticmethod
    def count_frequency(data):
        return Counter(data)

    def get_priority_queue(self, frequency):
        return [
            HuffmanNode(char, freq)
            for char, freq
            in frequency.items()
            if freq > self.min_freq
        ]

    def build_tree(self, data):
        frequency = self.count_frequency(data)
        priority_queue = self.get_priority_queue(frequency)
        heapq.heapify(priority_queue)

        while len(priority_queue) > 1:
            left = heapq.heappop(priority_queue)
            right = heapq.heappop(priority_queue)

            merged = HuffmanNode(None, left.freq + right.freq)
            merged.left = left
            merged.right = right

            heapq.heappush(priority_queue, merged)

        self.root = priority_queue[0]

    def generate_codes(self, node=None, prefix=""):
        if node is None:
            node = self.root
            self.code_book.clear()

        if node is not None:
            if node.char is not None:
                self.code_book[node.char] = prefix
            if node.left is not None:
                self.generate_codes(node.left, prefix + "0")
            if node.right is not None:
                self.generate_codes(node.right, prefix + "1")

    def encode(self, data):
        self.build_tree(data)
        self.generate_codes()
        return ''.join(self.code_book[char] for char in data), self.code_book

    def decode(self, encoded_data, code_book):
        reverse_code_book = {v: k for k, v in code_book.items()}
        current_code = ""
        decoded_data = []

        for bit in encoded_data:
            current_code += bit
            if current_code in reverse_code_book:
                decoded_data.append(reverse_code_book[current_code])
                current_code = ""

        return ''.join(decoded_data)


class ExtendedHuffman(Huffman):
    def __init__(self, min_phrase_length=2, max_phrase_length=5):
        super().__init__()
        self.min_phrase_length = min_phrase_length
        self.max_phrase_length = max_phrase_length
        self.min_freq = 1

    def count_frequency(self, data):
        frequency = super().count_frequency(data)
        length = len(data)
        for size in range(self.min_phrase_length, self.max_phrase_length + 1):
            for i in range(length - size + 1):
                phrase = data[i:i + size]
                frequency[phrase] += 1
        return frequency


def calculate_size_in_bytes(data):
    return len(data)


def calculate_compressed_size_in_bytes(encoded_data):
    size_in_bits = len(encoded_data)
    size_in_bytes = (size_in_bits + 7) // 8
    return size_in_bytes


# # data = "this is an example of a huffman tree with extended dictionary capabilities."
# data = "this is an example of a huffman tree with extended dictionary capabilities."
# # data = "this is an example of a huffman tree"
# huffman = ExtendedHuffman()
#
# encoded_data, code_book = huffman.encode(data)
# print("Encoded:", encoded_data)
#
# decoded_data = huffman.decode(encoded_data, code_book)
# print("Decoded:", decoded_data)
#
# original_size = calculate_size_in_bytes(data)
# compressed_size = calculate_compressed_size_in_bytes(encoded_data)
#
# print("Original size:", original_size, "bytes")
# print("Compressed size:", compressed_size, "bytes")
# print("Compression ratio:", original_size / compressed_size)
