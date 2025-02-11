import json
import os

def filter_existing_images(json_file_path):
    # Чтение JSON файла
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Фильтрация записей
    filtered_data = [entry for entry in data if os.path.exists(entry['image'])]

    # Сохранение отфильтрованных данных обратно в файл
    with open('captions.json', 'w', encoding='utf-8') as file:
        json.dump(filtered_data, file, ensure_ascii=False, indent=4)

# Пример использования функции
filter_existing_images('captions.json')
