import json
from csv import DictReader
class Reader:
    @staticmethod
    def read_csv(path: str) -> list:
        with open(path, mode='r', encoding='utf-8') as file:
            reader = DictReader(file, delimiter=',')
            return [{k: (None if v == 'NULL' else v) for k, v in row.items()} for row in reader]

    @staticmethod
    def read_json(path: str) -> dict:
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)