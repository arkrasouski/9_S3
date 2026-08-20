Создать пользователя для проверки записи

Настройте алиас для вашего сервера:

`mc alias set myminio http://localhost:9000 YOUR_ACCESS_KEY YOUR_SECRET_KEY`

`mc admin user add myminio НОВЫЙ_ACCESS_KEY НОВЫЙ_SECRET_KEY`

Для тестирования доступа "Любой мог читать файлы":
Добавить в инициализацию:

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