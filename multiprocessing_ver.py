import multiprocessing                                                              # Модуль для роботи з багатопроцесорністю
from collections import defaultdict                                                 # defaultdict для зручного зберігання результатів
from pathlib import Path                                                            # Модуль для роботи з файловими шляхами
import os                                                                           # Модуль для роботи з операційною системою
import time                                                                         # Модуль для вимірювання часу виконання
import traceback                                                                    # Модуль для відображення стеку викликів у випадку помилки
import chardet                                                                      # Модуль для автоматичного визначення кодування файлів


def search_in_file(file_path, keywords, results_queue):                             # Функція для пошуку ключових слів у файлі
    try:
                                                                                     
        with open(file_path, 'rb') as f:                                            # Відкриваємо файл у бінарному режимі
            raw_data = f.read()  
            result = chardet.detect(raw_data)                                       # Виконуємо визначення кодування
            encoding = result['encoding']   

                                                                                    # Читання файлу з визначеним кодуванням
        with open(file_path, 'r', encoding=encoding, errors='replace') as file:     # Відкриваємо файл у текстовому режимі
            content = file.read()   
            print(f"Processing file: {file_path} (Encoding: {encoding})")  
            for keyword in keywords:                                                # Перебираємо ключові слова
                if keyword in content:                                              # Якщо ключове слово знайдено у вмісті
                    print(f"Keyword '{keyword}' found in {file_path}")              # Логуємо знайдене ключове слово
                    results_queue.put((keyword, str(file_path)))                    # Додаємо результат у чергу
    except Exception as e:                                                          # Обробляємо можливі помилки
        print(f"Error processing file {file_path}: {e}")   
        traceback.print_exc()                                                       # Виводимо стек викликів помилки

def process_task(files, keywords, results_queue):                                   # Завдання для окремого процесу
    for file in files:   
        search_in_file(file, keywords, results_queue)                               # Викликаємо функцію для пошуку


def main_multiprocessing(file_paths, keywords):                                     # Основна функція для багатопроцесорної обробки
    start_time = time.time()                                                        # Вимірюємо часу виконання

                                                                # Визначаємо кількість процесорів, але не більше, ніж кількість файлів
    num_processes = min(len(file_paths), os.cpu_count())        # Визначаємо кількість доступних процесів

                                                                # Використовуємо Manager для створення черги для обміну даними між процесами
    manager = multiprocessing.Manager()  
    results_queue = manager.Queue()                             # Створюємо чергу для зберігання результатів
    results = defaultdict(list)                                 # Словник для зберігання результатів

                                                                # Розподіляємо файли між процесами
    chunk_size = max(1, len(file_paths) // num_processes)       # Визначаємо розмір частини для кожного процесу
    processes = []                                              # Список для зберігання створених процесів

    for i in range(num_processes):                              # Створюємо та запускаємо процеси
        start_index = i * chunk_size   
        end_index = None if i == num_processes - 1 else (i + 1) * chunk_size   
        process_files = file_paths[start_index:end_index]       # Вибираємо файли для процесу
        process = multiprocessing.Process(target=process_task, args=(process_files, keywords, results_queue))  # Створюємо новий процес
        processes.append(process)   
        process.start()                                         # Запускаємо процес

                                                                # Очікуємо завершення всіх процесів
    for process in processes:   
        process.join()                                          # Для кожного процесу чекаємо, поки процес завершиться

                                                                # Збираємо результати з черги
    while not results_queue.empty():   
        keyword, file_path = results_queue.get()                # Поки черга не порожня отримуємо результат з черги
        results[keyword].append(file_path)                      # Додаємо шлях до файлу до відповідного ключового слова

    end_time = time.time()                                      # Вимірюємо часу завершення
    print(f"Total execution time: {end_time - start_time} seconds")  # Виводимо загальний час виконання

    return results                                              # Повертаємо результати


if __name__ == '__main__':
    file_paths = list(Path("library").glob("*.txt"))            # Отримуємо список всіх текстових файлів у папці library
    keywords = ["owl", "wizard", "Hogwarts", "Voldemort"]       # Наші пошукові ключові слова

    print(f"File paths: {file_paths}\n")                        # Виводимо список файлів

                                                                # Виклик багатопроцесорної функції
    results = main_multiprocessing(file_paths, keywords)        # Виконуємо пошук

                                                                # Виводимо результати пошуку
    for keyword, files in results.items():    
        print(f"\nKeyword: '{keyword}' found in files:")   
        for file in files:                                      # Перебираємо файли, де знайдено ключове слово
            print(f" - {file}")                                 # Виводимо шлях до файлу
