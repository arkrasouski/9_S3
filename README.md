## Для запуска необходимо:
1. Создать `.env` файл с параметрами для minio s3
```
WSL_IP=localhost # Переменная создана исключительно для моей разработки через WSL для связи с Windows
MINIO_USER=admin
MINIO_PASSWORD=admin123
ART_USER_PASSWORD=artuserpass
```

2. Создать директорию `files`
В нее положить тестовые файлы для проверки скриптов (`test.txt`, `myfile.txt`)

3. В `files` создать `archive` (для задания 3)

4. В корне проекта создать папку `tmp` для временных файлов пайплайна

5. В качестве фильтрации pandas я брал CSV файл из модуля про dbt `smartphone_cleaned_v5.csv` им я тестировал работу пайплайна

## Вспомогательные настройки для тестирования правовой политики

### Создать пользователя для проверки записи

Настройте алиас для вашего сервера:

`mc alias set myminio http://localhost:9000 YOUR_ACCESS_KEY YOUR_SECRET_KEY`

`mc admin user add myminio НОВЫЙ_ACCESS_KEY НОВЫЙ_SECRET_KEY`

### Для тестирования доступа "Любой мог читать файлы":
Добавить в инициализацию класса `AsyncObjectStorage` конфиг (и `None` сделать **юзера и пароль**):

```
from botocore import UNSIGNED
from botocore.config import Config

self._auth = {
            "aws_access_key_id": None, # логин
            "aws_secret_access_key": None, # пароль
            "endpoint_url": endpoint,
            "config":Config(signature_version=UNSIGNED),
        }
```