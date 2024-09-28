import threading                                                      # Модуль для роботи з потоками
from collections import defaultdict                                   # defaultdict для зберігання результатів
from pathlib import Path                                              # Модуль для роботи з файлами та шляхами
import time                                                           # Модуль для вимірювання часу виконання
import traceback                                                      # Модуль для обробки помилок
import chardet                                                        # chardet для автоматичного визначення кодування

def search_in_file(file_path, keywords, results):                     # Функція для пошуку ключових слів у файлі
    try:
         
        with open(file_path, 'rb') as f:                              # Відкриваємо файл у бінарному режимі для визначення кодування
            raw_data = f.read()                               
            result = chardet.detect(raw_data)                         # Виконуємо визначення кодування
            encoding = result['encoding']                     

                                                                   # Читання файлу з визначеним кодуванням
        with open(file_path, 'r', encoding=encoding, errors='replace') as file:  # Відкриваємо файл у текстовому режимі
            content = file.read()                                     # Читаємо весь вміст файлу
            print(f"Processing file: {file_path} (Encoding: {encoding})")  
            for keyword in keywords:                                  # Перебираємо ключові слова
                if keyword in content:                                # Якщо ключове слово знайдено у вмісті
                    print(f"Keyword '{keyword}' found in {file_path}")  # Логуємо знайдене ключове слово
                    results[keyword].append(str(file_path))           # Додаємо результат до словника
    except Exception as e:                                            # Обробляємо можливі помилки
        print(f"Error processing file {file_path}: {e}")              # Виводимо повідомлення про помилку
        traceback.print_exc()                                         # Друкуємо деталі помилки


def thread_task(files, keywords, results):                            # Завдання для окремого потоку
    for file in files:                                                # Перебираємо всі файли, передані цьому потоку
        search_in_file(file, keywords, results)                       # Викликаємо функцію пошуку ключових слів у кожному файлі


def main_threading(file_paths, keywords):                             # Основна функція для багатопотокової обробки
    start_time = time.time()                                          # Починаємо вимірювання часу виконання

    
    num_threads = 8                                                   # Встановлюємо кількість потоків на 8 - це число визначає кількість одночасних потоків для виконання***

    results = defaultdict(list)                                       # Створюємо словник для зберігання результатів
    threads = []                                                      # Список для зберігання об'єктів потоків

                                                                      # Розподіляємо файли між потоками
    chunk_size = max(1, len(file_paths) // num_threads)               # Визначаємо розмір порції файлів для кожного потоку

    for i in range(num_threads):                                      # Створюємо потоки
        start_index = i * chunk_size                          
        end_index = None if i == num_threads - 1 else (i + 1) * chunk_size  
        thread_files = file_paths[start_index:end_index]              # Файли для поточного потоку
        thread = threading.Thread(target=thread_task, args=(thread_files, keywords, results))  # Створюємо потік і передаємо йому файли та ключові слова
        threads.append(thread)                                        # Додаємо потік до списку
        thread.start()                                                # Запускаємо потік

    # Очікуємо завершення всіх потоків
    for thread in threads:                                            # Проходимо по всіх потоках
        thread.join()                                                 # Чекаємо, поки кожен потік завершить роботу

    end_time = time.time()                                            # Завершуємо вимірювання часу
    print(f"Total execution time: {end_time - start_time} seconds")   # Виводимо загальний час виконання
 
    return results                                                    # Повертаємо результати

if __name__ == '__main__':
    # Приклад виклику
    file_paths = list(Path("library").glob("*.txt"))                  # Отримуємо всі файли .txt з теки "library"
    keywords = ["owl", "wizard", "Hogwarts", "Voldemort"]             # Наші пошукові ключові слова

    print(f"File paths: {file_paths}\n")                              # Виводимо список файлів

                                                                      # Виклик багатопотокової функції
    results = main_threading(file_paths, keywords)                    # Викликаємо основну функцію для пошуку

                                                                      # Виводимо результати пошуку
    for keyword, files in results.items():                    
        print(f"\nKeyword: '{keyword}' found in files:")     
        for file in files:                                    
            print(f" - {file}")                                       # Виводимо шлях до файлу
