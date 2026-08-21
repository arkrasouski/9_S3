
import asyncio
import csv
import gzip
from pathlib import Path
import shutil

from watchdog.events import FileSystemEventHandler
import pandas as pd

from utils.async_object_storage import AsyncObjectStorage

class FilesHandler(FileSystemEventHandler):
    """
    Обработчик который следит за папкой files
    И запускает пайплайн при появлении новых файлов
    """
    def __init__(self, s3: AsyncObjectStorage):
        self.s3 = s3

    @staticmethod
    def work(event):
        # отслеживаем только csv файлы
        flag = False
        suffix = ('csv',)
        if not event.is_directory and event.src_path.endswith(suffix):
            flag = True
        return flag

    def _filter_csv(self, file_path: Path, log_file: bytes) -> None:
        """Сохраняем только модели с nfc"""
        df = pd.read_csv(file_path)
        print(f'Число строк исходного файла: {len(df)}', file=log_file)
        df = df.loc[df['has_nfc']]
        print(f'Число строк файла после фильтрации: {len(df)}', file=log_file)
        tmp_file_path = Path(f'./tmp/{file_path.name}')
        df.to_csv(tmp_file_path)
        print("Файл записан во временную директорию", file=log_file)
        return tmp_file_path

    def _gzip_file(self, file_name: str):
        with open(f'./files/{file_name}', 'rb') as f_in:
            with gzip.open(f'./files/archive/{file_name}.gz', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

    def on_created(self, event):
        # обрабатываем событие `on_created`
        if self.work(event):
            file_path = Path(event.src_path)
            log_path = Path('./tmp/log.txt')
            with open(log_path, 'w') as log_file:
                print(f"Событие {event.event_type} по пути {file_path}. Запускаем pipeline", file=log_file)
                filtered_file_path = self._filter_csv(file_path, log_file)
                asyncio.run(self.s3.send_file(filtered_file_path, 'with_nfc'))
                print("Файл записан в хранилище", file=log_file)
                self._gzip_file(file_path.name)
                file_path.unlink() #Удалить файл
                filtered_file_path.unlink() #Удалить файл
                print("Исходник заархивирован", file=log_file)
                
            asyncio.run(self.s3.send_file(log_path))
            log_path.unlink()
            
