import asyncio

from utils.async_object_storage import AsyncObjectStorage



# s3 = AsyncObjectStorage(
#     key_id='admin',
#     secret='admin123',
#     endpoint='http://localhost:19000',
#     container='test'
# )

# asyncio.run(s3.send_file('./test.txt'))
from minio import Minio

client = Minio(
    "127.0.0.1:19000",
    access_key="admin",
    secret_key="admin123",
    secure=False
)

for obj in client.list_objects("test", recursive=True):
    print(obj.object_name, obj.size)