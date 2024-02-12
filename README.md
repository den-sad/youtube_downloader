# Телеграмм бот по загрузке видо из YouTube по ссылке на видео или плейлист
Бот загружает указанные видео, перемещает их в ваше облако OwnCloud и формирует ссылку на загрузку

## Использование локально

Склонируйте проект

```
git clone https://git.virtual-it.ru:3000/den/youtube_downloader.git
```

Создайте и запустите виртуальное окружение

```
cd youtube_downloader
python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

Создайте файл окружения .env

Запустите приложение

```
python3 app.py
```

Видео загружается в каталог проекта в папку video

## Запуск с использованием docker compose

```
git clone https://git.virtual-it.ru:3000/den/youtube_downloader.git
```

Создайте файл окружения .env

Соберите образ и запустите его

```
docker compose  -f 'docker-compose.yml'  up --build  
```

## Переменные для запуска проекта, файл .env

LOG_PATH = <LOG_PATH>

VIDEO_PATH = </VIDEO_PATH>

BOT_API_KEY = <telegram bot api key>

ALLOWED_IDS = <ID1, ID2, ID3>

OWNCLOUD_URL = <URL to Owncloud>

OWNCLOUD_DIR = <Downloads>

OWNCLOUD_USER = <USER>

OWNCLOUD_PASS = <PASSWORD>

## Переменные для CI-CD pipeline

GOTIFY_URL - адрес серва уведомлений Gotify, пример gotify.host.com

GOTIFY_KEY - api ключ для уведомлений через Gotify

GITEA - адрес GIT сервера, пример 192.168.1.2:22

REGISTRY - адрес docker репозитария, пример docker.host.com

DEPLOY_SERVER - адрес сервера для развертывания бота, пример user@192.168.1.3


# TODO
Использование индивидуальных параметров облака для каждого пользователя
Возможность указать настройки хранилищи пользователя через бота