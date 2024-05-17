import pandas as pd
import pathlib
from protobuf import iot_temp_pb2
from collections import defaultdict
from common.q import HuffmanAdaptiveCodebook
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
import re
import string
import random
import time
import json

datasets_dir = pathlib.Path('datasets')


def save_codebook(serialized_codebook, filename):
    with open(filename, 'wb') as f:
        f.write(serialized_codebook)


def load_codebook(filename):
    with open(filename, 'rb') as f:
        serialized_codebook = f.read()
    return serialized_codebook


def process_data_sample(data, codebook, phrase_length, special_patterns):
    try:
        encoded = codebook.encode_data(data, phrase_length, special_patterns)
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


def prepare_iot_temp_df():
    df = pd.read_csv(datasets_dir / 'iot_temp.csv')
    df = df.astype({'id': str, 'room_id/id': str, 'noted_date': str, 'out/in': str, 'temp': int})
    df.dropna(subset=['temp'], inplace=True)
    df['temp'] = df['temp'].astype(int)
    print('DF VALIDATION COMPLETED')
    return df


def serialize_row(row):
    pb = iot_temp_pb2.LogEntry(
        entity=row['id'],
        user=row['room_id/id'],
        timestamp=row['noted_date'],
        temperature=row['temp'],
        status=row['out/in']
    )
    return pb.SerializeToString()


def serialize_rational(row):
    # Convert string to datetime object
    date_time_obj = datetime.strptime(row['noted_date'], '%d-%m-%Y %H:%M')
    # Calculate the Unix timestamp
    timestamp = (date_time_obj - datetime(1970, 1, 1)).total_seconds()
    pb = iot_temp_pb2.LogEntryRational()
    pb.entity = row['id']
    pb.user = row['room_id/id']
    pb.timestamp.FromSeconds(int(timestamp))
    pb.temperature = row['temp']
    pb.status = row['out/in']
    return pb.SerializeToString()




def serialize_normal(row):
    # Convert string to datetime object
    date_time_obj = datetime.strptime(row['noted_date'], '%d-%m-%Y %H:%M')
    # Calculate the Unix timestamp
    timestamp = (date_time_obj - datetime(1970, 1, 1)).total_seconds()

    message_source_map = {
        "__export__.temp_log_": "TEMP_LOG"
    }
    user_map = {
        "Room Admin": "ROOM_ADMIN"
    }

    tick_hash = re.search(r'(\d+)_\w+', row['id']).group(1)
    message_hash = re.search(r'_([0-9a-fA-F]+)$', row['id']).group(1)

    pb = iot_temp_pb2.LogEntryNormal()
    pb.messageSource = message_source_map[row['id'][:20]]
    pb.tickHash = int(tick_hash)
    pb.messageHash = int(message_hash, 16)
    pb.user = user_map[row['room_id/id']]
    pb.timestamp.FromSeconds(int(timestamp))
    pb.temperature = row['temp']
    pb.status = "In"

    return pb.SerializeToString()


def update_encoding_stats(encoding_maps, json_size, original_size, encoded_size):
    encoding_maps[original_size][0] += json_size
    encoding_maps[original_size][1] += encoded_size
    encoding_maps[original_size][2] += 1

    if encoding_maps[original_size][3] == -1:
        encoding_maps[original_size][3] = encoded_size
    else:
        encoding_maps[original_size][3] = min(encoding_maps[original_size][3], encoded_size)

    encoding_maps[original_size][4] = max(encoding_maps[original_size][4], encoded_size)


def serialize_normal_random():
    message_source_map = {
        "__export__.temp_log_": "TEMP_LOG"
    }
    user_map = {
        "Room Admin": "ROOM_ADMIN"
    }

    start_date = datetime(2020, 1, 1)
    end_date = datetime(2030, 12, 31)

    start_seconds = int(time.mktime(start_date.timetuple()))
    end_seconds = int(time.mktime(end_date.timetuple()))

    random_seconds = random.randint(start_seconds, end_seconds)
    random_int32 = random.randint(0, 999_999)
    random_temp = random.randint(0, 99)

    hex_characters = string.hexdigits[:-6]  # Exclude uppercase letters
    random_hex = ''.join(random.choice(hex_characters) for _ in range(8))
    random_status = random.choice(["In", "Out"])

    date_time = datetime.utcfromtimestamp(random_seconds)
    formatted_date_time = date_time.strftime("%d-%m-%Y %H:%M")

    jsd = {
        "id": f"__export__.temp_log_{random_int32}_{hex_characters}",
        "room_id/id": "Room Admin",
        "noted_date": formatted_date_time,
        "temp": random_temp,
        "out/in": random_status
    }
    serialized_json_str = json.dumps(jsd, separators=(',', ':'))
    result = len(serialized_json_str.encode('utf-8'))

    pb = iot_temp_pb2.LogEntryNormal()
    pb.messageSource = message_source_map["__export__.temp_log_"]
    pb.tickHash = random_int32
    pb.messageHash = int(random_hex, 16)
    pb.user = user_map["Room Admin"]
    pb.timestamp.FromSeconds(random_seconds)
    pb.temperature = random_temp
    pb.status = random_status

    return result, pb.SerializeToString()


def prepare_iot_temp(mode, book_mode, max_phrase_length, special_patterns, filename):
    if mode == 'row':
        serializator_func = serialize_row
    elif mode == 'normal':
        serializator_func = serialize_normal
    else:
        serializator_func = serialize_rational

    df = prepare_iot_temp_df()

    start_timestamp = datetime.now()
    with ProcessPoolExecutor() as executor:
        data_samples = list(executor.map(serializator_func, [dict(row) for _, row in df.iterrows()]))
    print(f'DATA SAMPLES COLLECTION COMPLETED ({datetime.now() - start_timestamp} sec)')

    if book_mode == 'generate':
        start_timestamp = datetime.now()
        codebook = HuffmanAdaptiveCodebook()
        frequencies = codebook.calculate_phrase_frequencies(data_samples, max_phrase_length, special_patterns)
        root = codebook.build_huffman_tree(frequencies)
        codebook.generate_codes(root)
        print(f'CODEBOOK GENERATED ({datetime.now() - start_timestamp} sec)')

        start_timestamp = datetime.now()
        serialized_codebook = codebook.serialize_codebook()
        print(f'CODEBOOK SERIALIZED ({datetime.now() - start_timestamp} sec)')
        print(f'CODEBOOK SIZE: {len(serialized_codebook)} BYTES')

        start_timestamp = datetime.now()
        save_codebook(serialized_codebook, filename)
        print(f'CODEBOOK SAVED ({datetime.now() - start_timestamp} sec)')

    else:
        start_timestamp = datetime.now()
        serialized_codebook = load_codebook()
        print(f'BOOK LOADED ({datetime.now() - start_timestamp} sec)')

        start_timestamp = datetime.now()
        codebook = HuffmanAdaptiveCodebook(max_phrase_length=max_phrase_length)
        codebook.deserialize_codebook(serialized_codebook)
        print(f'INIT AND DESEREALIZATION TIME ({datetime.now() - start_timestamp} sec)')

    # start_timestamp = datetime.now()
    # serialized_codebook = codebook.serialize_codebook()
    # print(f'CODEBOOK SERIALIZED ({datetime.now() - start_timestamp} sec)')
    # print(f'CODEBOOK SIZE: {len(serialized_codebook)} BYTES')
    #
    # start_timestamp = datetime.now()
    # save_codebook(serialized_codebook)
    # print(f'CODEBOOK SAVED ({datetime.now() - start_timestamp} sec)')
    #
    # start_timestamp = datetime.now()
    # new_codebook = HuffmanAdaptiveCodebook(max_phrase_length=20)
    # new_codebook.deserialize_codebook(serialized_codebook)
    # print(f'CODEBOOK DESERIALIZED ({datetime.now() - start_timestamp} sec)')
    #
    # print("Codebooks are identical:", codebook.huffman_codes == new_codebook.huffman_codes)

    encoding_maps = defaultdict(lambda: [0, 0, 0, -1, -1])
    compressing_errors = 0
    results = []
    for _ in range(10000):
        try:
            original_size, serialized = serialize_normal_random()
            encoded_message = codebook.encode_data(serialized, max_phrase_length, special_patterns)
            serialized_size = len(serialized)
            encoded_size = (len(encoded_message) + 7) // 8
            is_correct = True

            results.append({
                'json_size': original_size,
                'original_size': serialized_size,
                'encoded_size': encoded_size,
                'is_correct': is_correct
            })

        except Exception as e:
            results.append({
                'error': str(e),
                'original_size': None,
                'encoded_size': None,
                'is_correct': False
            })

    # for key, value in result.items():
    #     print(f'{key}: {dict(value)}')
    #
    # data_samples = data_samples[:1]
    # results = []
    # for data in data_samples:
    #     results.append(process_data_sample(data, codebook, max_phrase_length, special_patterns))
    # print(
    #     f'Processed {len(data_samples)} messages [{len(codebook.huffman_codes)} book]: ({datetime.now() - start_timestamp} sec)')

    for result in results:
        if 'error' in result:
            print(f"Error processing data: {result['error']}")
            continue
        if not result['is_correct']:
            compressing_errors += 1
            continue
        update_encoding_stats(encoding_maps, result['json_size'], result['original_size'], result['encoded_size'])

    for key, value in encoding_maps.items():
        print(f'"{key}": {value},')

    # print(codebook.huffman_codes)


if __name__ == '__main__':
    mode = 'normal'
    book_mode = 'generate'
    max_phrase_length = 1
    filename = datasets_dir / 'huffman_codebook_normal_G.bin'
    special_patterns = []
    prepare_iot_temp(mode, book_mode, max_phrase_length, special_patterns, filename)
