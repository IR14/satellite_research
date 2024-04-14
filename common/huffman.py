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
        # Предполагается, что data теперь байтовый массив
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
        return ''.join(self.code_book[b] for b in data), self.code_book

    def decode(self, encoded_data, code_book):
        reverse_code_book = {v: k for k, v in code_book.items()}
        current_code = ""
        decoded_data = []

        for bit in encoded_data:
            current_code += bit
            if current_code in reverse_code_book:
                decoded_data.append(reverse_code_book[current_code])
                current_code = ""

        # Преобразование списка байтов в байтовую строку
        return bytes(decoded_data)
