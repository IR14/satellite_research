from collections import defaultdict, Counter
from heapq import heappush, heappop
from concurrent.futures import ThreadPoolExecutor
from bitarray import bitarray
import struct
import pickle


class Node:
    def __init__(self, left=None, right=None, phrase=None):
        self.left = left
        self.right = right
        self.phrase = phrase


class HuffmanAdaptiveCodebook:
    def __init__(self, max_phrase_length=1):
        self._huffman_codes = {}
        self._max_phrase_length = max_phrase_length

    def calculate_frequencies_part (self, data):
        frequency = defaultdict(int)
        n = len(data)
        seen_phrases = {}
        for length in range(1, self._max_phrase_length + 1):
            for i in range(n - length + 1):
                phrase = data[i:i + length]
                if phrase not in seen_phrases:
                    seen_phrases[phrase] = True
                    frequency[phrase] += 1
        return frequency

    def calculate_all_phrase_frequencies(self, data_samples):
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(self.calculate_frequencies_part, data_samples))

        combined_frequency = Counter()

        for result in results:
            combined_frequency.update(result)

        filtered_frequencies = {
            phrase: freq
            for phrase, freq
            in combined_frequency.items()
            if freq > 1 or len(phrase) == 1
        }

        dominant_threshold = len(data_samples) * 0.3

        adjusted_frequencies = Counter(filtered_frequencies)
        for phrase, freq in sorted(combined_frequency.items(), key=lambda x: -len(x[0])):
            if freq < dominant_threshold:
                continue
            phrase_len = len(phrase)
            for sub_len in range(1, phrase_len):
                for start in range(phrase_len - sub_len + 1):
                    sub_phrase = phrase[start:start + sub_len]
                    if sub_phrase not in adjusted_frequencies:
                        continue
                    adjusted_frequencies[sub_phrase] = max(
                        adjusted_frequencies[sub_phrase] - freq // 2, 1
                    )

        return adjusted_frequencies

    @staticmethod
    def build_huffman_tree(frequencies):
        heap = []
        count = 0
        for phrase, freq in frequencies.items():
            heappush(heap, (freq, count, Node(phrase=phrase)))
            count += 1

        while len(heap) > 1:
            freq1, _count1, left = heappop(heap)
            freq2, _count2, right = heappop(heap)
            heappush(heap, (freq1 + freq2, count, Node(left=left, right=right)))
            count += 1

        root = heappop(heap)[2]
        return root

    def generate_codes(self, node, prefix=bitarray()):
        if node.phrase is not None:
            self._huffman_codes[node.phrase] = prefix
            return
        if node.left:
            self.generate_codes(node.left, prefix + bitarray('0'))
        if node.right:
            self.generate_codes(node.right, prefix + bitarray('1'))

    def encode_data(self, data):
        encoded = bitarray()
        index = 0
        while index < len(data):
            best_ratio = 0
            best_phrase = None
            best_code = None

            for length in range(1, self._max_phrase_length + 1):
                if index + length > len(data):
                    break
                phrase = data[index:index + length]
                if phrase in self._huffman_codes:
                    code_length = len(self._huffman_codes[phrase])
                    ratio = length / code_length
                    if ratio > best_ratio:
                        best_ratio = ratio
                        best_phrase = phrase
                        best_code = self._huffman_codes[phrase]
            if best_phrase:
                encoded.extend(best_code)
                index += len(best_phrase)
            else:
                index += 1
        return encoded

    def decode_data(self, encoded_data):
        inverted_codebook = {code.to01(): phrase for phrase, code in self._huffman_codes.items()}
        decoded_output = bytearray()
        temp_code = bitarray()
        for bit in encoded_data:
            temp_code.append(bit)
            temp_code_str = temp_code.to01()
            if temp_code_str in inverted_codebook:
                decoded_output.extend(inverted_codebook[temp_code_str])
                temp_code.clear()
        return bytes(decoded_output)

    def serialize_codebook(self):
        serializable_codebook = {phrase: (code.tobytes(), len(code)) for phrase, code in self._huffman_codes.items()}
        return struct.pack('>I', len(serializable_codebook)) + pickle.dumps(serializable_codebook)

    def deserialize_codebook(self, serialized_codebook):
        length = struct.unpack('>I', serialized_codebook[:4])[0]
        codebook = pickle.loads(serialized_codebook[4:])
        for phrase, (code_bytes, length) in codebook.items():
            bit_code = bitarray()
            bit_code.frombytes(code_bytes)
            bit_code = bit_code[:length]
            self._huffman_codes[phrase] = bit_code
