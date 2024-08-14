import json


def save_to_json(result, file_path='../data/predicted_result.json'):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)


def save_to_bd():
    pass