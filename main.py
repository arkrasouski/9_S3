import asyncio
import os
import boto3
from dotenv import load_dotenv
from minio import MinioAdmin
from utils.async_object_storage import AsyncObjectStorage
from minio.credentials import StaticProvider
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
#     secret=os.getenv('ART_USER'),
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
# Выдача прав анонимным пользователям
#asyncio.run(s3.set_bucket_public_read())
# Проверка политики
#asyncio.run(s3.get_bucket_policy())

# Скачивание из и загрузка в хранилище
asyncio.run(s3.fetch_file('test.txt', './files/test1112222.txt'))
asyncio.run(s3.send_file('./files/test1112222.txt'))

# Получение всех файлов в хранилище
# files = asyncio.run(s3.list_files())
# print(files)

# Проверка существования файла в хранилище
#is_file_exists = asyncio.run(s3.file_exists('test.txt'))
# print(is_file_exists)