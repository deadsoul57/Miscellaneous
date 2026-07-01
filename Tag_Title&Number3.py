# Шлях до папки береться з першого параметру при запуску
# Спочатку сортує всі аудіофайли за іменем (в алфавітному порядку), а потім під час обробки 
# додає два теги: Title (назва файлу) та Track Number (порядковий номер, починаючи з 1).
# Порядковий номер треку автоматично форматується із провідними нулями відповідно до 
# загальної кількості файлів у папці:
# Якщо файлів менше 100 (наприклад, 12), номери будуть: 01, 02, ... 12.
# Якщо файлів 100 або більше (наприклад, 150), номери автоматично стануть тризначними: 001, 002, ... 150.

# Якщо параметр force_three_digits увімкнено (True), то для першого треку завжди запишеться саме 001. 
# Якщо виставити False, програма сама порахує: для 50 файлів зробить формат 01, а для 200 файлів 
# автоматично зробить 001.

import argparse
from pathlib import Path
from mutagen import File
from mutagen.easyid3 import EasyID3

def fix_audio_tags_and_tracks(directory_path, force_three_digits=True):
    path = Path(directory_path)
    
    if not path.is_dir():
        print(f"Помилка: Шлях '{directory_path}' не є директорією або не існує.")
        return

    # Список підтримуваних розширень
    supported_extensions = {'.mp3', '.flac', '.m4a', '.ogg', '.wav'}
    
    # Збираємо всі підтримувані файли з папки
    audio_files = [
        f for f in path.iterdir() 
        if f.is_file() and f.suffix.lower() in supported_extensions
    ]
    
    # Сортуємо файли за іменем (в алфавітному порядку)
    audio_files.sort(key=lambda x: x.name.lower())
    # Сортування за датою файлу 
#    audio_files.sort(key=lambda x: x.stat().st_mtime)

    total_files = len(audio_files)
    if total_files == 0:
        print("У вказаній папці не знайдено підтримуваних аудіофайлів.")
        return

    # Визначаємо ширину номера треку (мінімум 3 символи для формату 001)
    if force_three_digits:
        track_padding = max(3, len(str(total_files)))
    else:
        track_padding = len(str(total_files))

    success_count = 0
    error_count = 0

    print(f"Каталог обробки: {path.resolve()}")
    print(f"Знайдено файлів: {total_files}")
    print(f"Формат номера:  {'0' * track_padding}")
    print("Починаємо обробку...\n" + "-"*50)

    for index, file_path in enumerate(audio_files, start=1):
        file_name_without_ext = file_path.stem
        track_number_str = str(index).zfill(track_padding)
        
        try:
            audio = File(file_path)
            
            if audio is None:
                if file_path.suffix.lower() == '.mp3':
                    audio = EasyID3(file_path)
                else:
                    print(f"[{track_number_str}] Не вдалося розпізнати формат: {file_path.name}")
                    error_count += 1
                    continue

            # Запис тегів залежно від формату
            if isinstance(audio, EasyID3) or file_path.suffix.lower() == '.mp3':
                if not isinstance(audio, EasyID3):
                    audio = EasyID3(file_path)
                audio['title'] = file_name_without_ext
                audio['tracknumber'] = track_number_str
            else:
                audio['title'] = file_name_without_ext
                audio['tracknumber'] = track_number_str

            audio.save()
            print(f"[{track_number_str}] Успішно: {file_path.name} -> Title: \"{file_name_without_ext}\"")
            success_count += 1
            
        except Exception as e:
            print(f"[{track_number_str}] Помилка обробки {file_path.name}: {e}")
            error_count += 1

    print("-"*50)
    print(f"Завершено! Успішно: {success_count}, Помилок: {error_count}")


if __name__ == "__main__":
    # Налаштування парсера аргументів командного рядка
    parser = argparse.ArgumentParser(
        description="Автоматичне заповнення тегів Title (іменем файлу) та Track Number (001, 002...) для аудіофайлів."
    )
    # Додаємо обов'язковий позиційний аргумент — шлях до папки
    parser.add_argument(
        "dir", 
        type=str, 
        help="Шлях до каталогу з аудіофайлами"
    )
    
    args = parser.parse_args()
    
    # Запуск основної функції з переданим шляхом. force_three_digits=True або False
    fix_audio_tags_and_tracks(args.dir, force_three_digits=False)
