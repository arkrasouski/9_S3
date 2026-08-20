import asyncio  

import json
from pathlib import Path

# Для создания асинхронного контекстного менеджера
from contextlib import asynccontextmanager

# Асинхронная версия boto3
from aiobotocore.session import get_session
from botocore import UNSIGNED
from botocore.config import Config
# Ошибки при обращении к API
from botocore.exceptions import ClientError  
from minio import Minio, MinioAdmin

class AsyncObjectStorage:
    def __init__(self, *, key_id: str, secret: str, endpoint: str, container: str):
        self._auth = {
            "aws_access_key_id": key_id, # логин
            "aws_secret_access_key": secret, # пароль
            #"config":Config(signature_version=UNSIGNED),
            "endpoint_url": endpoint,
        }
        self._bucket = container
        self._session = get_session() # сессия aiobotocore общая для экземпляра класса

    @asynccontextmanager
    async def _connect(self):
        """
        Создает объект подключения в рамках контекстного менджера
        """
        async with self._session.create_client("s3", **self._auth) as connection:
            yield connection # yield превращает функцию в генератор, который работает как контекстный менеджер

    async def send_file(self, local_source: str):
        """
        Загружает файлы из локальной файловой системы в бакет
        """
        file_ref = Path(local_source)
        target_name = file_ref.name
        async with self._connect() as remote:
            with file_ref.open("rb") as binary_data:
                await remote.put_object(
                    Bucket=self._bucket,
                    Key=target_name,
                    Body=binary_data
                )

    async def fetch_file(self, remote_name: str, local_target: str):
        """
        Скачивает файл из бакета в локальную систему
        """
        async with self._connect() as remote:
            response = await remote.get_object(Bucket=self._bucket, Key=remote_name)
            body = await response["Body"].read()
            with open(local_target, "wb") as out:
                out.write(body)

    async def remove_file(self, remote_name: str):
        """
        Удаляет файл из бакета
        """
        async with self._connect() as remote:
            await remote.delete_object(Bucket=self._bucket, Key=remote_name)

    async def list_files(self):
        """
        Возвращает список объектов в бакете
        """
        async with self._connect() as remote:
            paginator = remote.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(Bucket=self._bucket)
            files_list = []
            async for page in page_iterator:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        file_name = obj['Key']
                        #print(f"Объект: {file_name} (Размер: {obj['Size']} байт)")
                        files_list.append(file_name)
              
            return files_list

    async def file_exists(self, remote_name: str) -> bool:
        """
        Проверка существования файла в s3

        :param str remote_name: Имя файла в бакете

        :rtype: bool
        :return: Существует ли файл
        """
        return remote_name in await self.list_files()

    async def set_bucket_public_read(self):
        """Устанавливает политику публичного чтения анонимным пользователям через bucket policy."""
        async with self._connect() as client:
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{self._bucket}/*"]
                    }
                ]
            }

            try:
                await client.put_bucket_policy(
                    Bucket=self._bucket,
                    Policy=json.dumps(policy)
                )
                print(f"Политика публичного чтения успешно применена к бакету: {self._bucket}")
            except Exception as e:
                print(f"Ошибка при установке политики: {e}")

    async def get_bucket_policy(self):
        """Получает текущую политику бакета через S3 API."""
        async with self._connect() as client:
            try:
                response = await client.get_bucket_policy(Bucket=self._bucket)
                policy = json.loads(response['Policy'])
                print("Текущая политика бакета (JSON):")
                print(json.dumps(policy, indent=2))
                return policy
            except Exception as e:
                print(f"Бакет {self._bucket} не имеет политики или она не найдена: {e}")
                return None

    def set_write_policy_to_user(self, admin_client: MinioAdmin, user_name: str):
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "s3:PutObject",
                            "s3:GetObject",
                            "s3:DeleteObject",
                            "s3:ListBucket"
                        ],
                        "Resource": [
                            f"arn:aws:s3:::{self._bucket}",
                            f"arn:aws:s3:::{self._bucket}/*"
                        ]
                    }
                ]
            }

            try:
                admin_client.policy_add(
                    "write-policy",
                    policy=policy
                )

                # Назначить пользователю
                admin_client.policy_set(
                    'write-policy',
                    user=user_name
                )
                print(f"Политика записи успешно применена к бакету: {self._bucket} для пользователя: {user_name}")
            except Exception as e:
                print(f"Ошибка при установке политики: {e}")