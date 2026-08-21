import asyncio
import os
from pathlib import Path

from watchdog.observers import Observer
from dotenv import load_dotenv
from minio import MinioAdmin
from utils.async_object_storage import AsyncObjectStorage
from minio.credentials import StaticProvider

from utils.files_handler import FilesHandler
load_dotenv()

bucket_name = 'test'
endpoint = 'localhost:19000'

# Клиент для имитации админа
s3 = AsyncObjectStorage(
    key_id=os.getenv('MINIO_USER'),
    secret=os.getenv('MINIO_PASSWORD'),
    endpoint='http://localhost:19000',
    container=bucket_name
)

# Клиент для имитации случайнного пользователя
# s3 = AsyncObjectStorage(
#     key_id='art',
#     secret=os.getenv('ART_USER_PASSWORD'),
#     endpoint=f'http://{endpoint}',
#     container=bucket_name
# )

# Клиент для имитации анонимного пользователя
# s3 = AsyncObjectStorage(
#     key_id=None,
#     secret=None,
#     endpoint=f'http://{endpoint}',
#     container=bucket_name
# )


# Клиент админа для выдачи прав новому пользователю
# admin_client = MinioAdmin(
#     endpoint=endpoint,
#     credentials=StaticProvider(
#         access_key=os.getenv('MINIO_USER'),
#         secret_key=os.getenv('MINIO_PASSWORD'),
#     ),
#     secure=False
# )

# Выдача прав пользователю art
# s3.set_write_policy_to_user(admin_client, 'art')

async def main(s3: AsyncObjectStorage):
    # Выдача прав анонимным пользователям
    await s3.set_bucket_public_read()

    # Проверка политики
    await s3.get_bucket_policy()

    await s3.send_file('./files/test.txt')
    await s3.send_file('./files/myfile.txt')

    # Скачивание из и загрузка в хранилище
    await s3.fetch_file('test.txt', './files/test1112222.txt')
    await s3.send_file('./files/test1112222.txt')

    # Получение всех файлов в хранилище
    files = await s3.list_files()
    print(files)

    # Проверка существования файла в хранилище
    is_file_exists = await s3.file_exists('test.txt')
    print(is_file_exists)

    # Включаю версионирование
    await s3.enable_versioning()

    # Отправляю файл повторно
    await s3.send_file('./files/test.txt')

    # Скачиваю предыдущую версию
    await s3.download_previous_version("test.txt", './files/test_v1.txt')

    # Устанавливаю политику удаления старых файлов
    await s3.set_lifecycle_policy()

    # Проверяю политику удаления старых файлов
    await s3.get_lifecycle_policy()

#asyncio.run(main(s3))

handler = FilesHandler(s3=s3)
observer = Observer()

path = Path('./files/')
observer.schedule(handler, path=path, recursive=False)
observer.start()
try:
    while observer.is_alive(): # Проверяет, жив ли этот поток
        observer.join(1) # Ждет 1 секунду, пока observer работает, или пока не завершится
finally:
    observer.stop()
    observer.join() # Гарантирует, что все обработчики событий закончили работу