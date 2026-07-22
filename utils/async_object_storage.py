import asyncio  

from pathlib import Path

# Для создания асинхронного контекстного менеджера
from contextlib import asynccontextmanager

# Асинхронная версия boto3
from aiobotocore.session import get_session

# Ошибки при обращении к API
from botocore.exceptions import ClientError  


class AsyncObjectStorage:
    def __init__(self, *, key_id: str, secret: str, endpoint: str, container: str):
        self._auth = {
            "aws_access_key_id": key_id,
            "aws_secret_access_key": secret,
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