from config import ROOT_DIR
import os
import json
import time
import datetime

WORK_PATH = os.path.join(ROOT_DIR, 'results', 'data.json')


def import_data_json(path):
    if os.path.isfile(path):
        with open(path, 'r') as read_file:
            data_json = json.load(read_file)
        return data_json
    return None


times = import_data_json(WORK_PATH)

A = {'1': [223.38104060462243, datetime.datetime(2023, 5, 2, 10, 35, 52, tzinfo=datetime.timezone.utc),
           55.99853008293953, 33.840861940925734],
     '2': [100.40914981415015, datetime.datetime(2023, 5, 2, 12, 21, 11, tzinfo=datetime.timezone.utc),
           55.73941768709715, 39.00907665265173],
     '3': [177.33598701750958, datetime.datetime(2023, 5, 3, 1, 59, 48, tzinfo=datetime.timezone.utc),
           55.699793004848715, 34.57978993727292],
     '4': [146.2195582900112, datetime.datetime(2023, 5, 3, 3, 45, 9, tzinfo=datetime.timezone.utc), 55.89888475298285,
           39.74434770166017],
     '5': [229.70590843490012, datetime.datetime(2023, 5, 2, 18, 59, 39, tzinfo=datetime.timezone.utc),
           56.024773402791574, 33.74238938511751],
     '6': [90.18112422819789, datetime.datetime(2023, 5, 2, 20, 44, 59, tzinfo=datetime.timezone.utc),
           55.77189362104975, 38.849114254582545]}

