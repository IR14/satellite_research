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
    def __init__(self):
        self.root = None
        self.code_book = defaultdict(str)

    @staticmethod
    def count_frequency(data):
        return Counter(data)

    def build_tree(self, data):
        frequency = self.count_frequency(data)
        priority_queue = [HuffmanNode(char, freq) for char, freq in frequency.items()]
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

    @staticmethod
    def calculate_size_in_bytes(data):
        return len(data)

    @staticmethod
    def calculate_compressed_size_in_bytes(encoded_data):
        # Определяем размер в битах
        size_in_bits = len(encoded_data)
        # Переводим биты в байты
        size_in_bytes = (size_in_bits + 7) // 8  # Добавляем 7 для округления вверх
        return size_in_bytes


# Пример использования класса Huffman
# data = "this is an example of a huffman tree"
data = "this is an example of a huffman tree with extended dictionary capabilities."
huffman = Huffman()

encoded_data, code_book = huffman.encode(data)
print("Encoded:", encoded_data)

decoded_data = huffman.decode(encoded_data, code_book)
print("Decoded:", decoded_data)

original_size = huffman.calculate_size_in_bytes(data)
compressed_size = huffman.calculate_compressed_size_in_bytes(encoded_data)

print("Original size:", original_size, "bytes")
print("Compressed size:", compressed_size, "bytes")
print("Compression ratio:", original_size / compressed_size)