Проект доступен по адресу [https://janedomain.ru/](https://janedomain.ru/)

![example workflow](https://github.com/turbonyasha/foodgram/actions/workflows/main.yml/badge.svg)

<img src="https://img.shields.io/badge/Python-blue?logo=python&logoColor=white&style=for-the-badge"><img src="https://img.shields.io/badge/Django-darkgreen?logo=django&logoColor=white&style=for-the-badge"><img src="https://img.shields.io/badge/Nginx-green?logo=nginx&logoColor=white&style=for-the-badge"><img src="https://img.shields.io/badge/Docker-blue?logo=docker&logoColor=white&style=for-the-badge"><img src="https://img.shields.io/badge/dockerhub-darkblue?logo=docker&logoColor=white&style=for-the-badge"><img src="https://img.shields.io/badge/Postgresql-lightblue?logo=postgresql&logoColor=white&style=for-the-badge">

# ★ FOODGRAM: платформа для хранения рецептов ★

Пользователи получают возможность делиться своими любимыми рецептами, а также хранить понравившиеся рецепты в Избранном и получать список необходимых продуктов для приготовления желаемых рецептов.
Похвастайся своим невероятным рецептом уже сегодня!

## Содержание
✔ [Описание проекта Foodgram](#описание-проекта)
✔ [API спецификация проекта Foodgram](#API-проекта)
✔ [Развернуть проект Foodgram локально без Docker](#развернуть-проект-Foodgram-локально-без-Docker)
✔ [Развернуть проект Foodgram на своем сервере с помощью Docker](#развернуть-проект-Foodgram-на-своем-сервере-с-помощью-Docker)
✔ [Настроить CI/CD проекта Foodgram на GitHub Actions c DockerHUB](#Настроить-CI/CD-Foodgram-на-GitHub-Actions-c-DockerHUB)
✔ [Автор проекта](#автор-проекта)


## ◑ Описание проекта
«Фудграм» — сайт, на котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## ◑ API проекта
Полная API спецификация проекта доступна по эндпоинту [/api/docs/](https://janedomain.ru/api/docs/) в формате Redoc.

## ◑ Развернуть проект Foodgram локально без Docker
### 1. Клонируйте репозиторий и перейдите в него в терминале:
```
git clone git@github.com:turbonyasha/foodgram.git
cd foodgram
```

### 2. Настройте и запустите /frontend:
Установите Node.js версии v16.20.2, используя дистрибутивы и инструкции с [официального сайта проекта.](https://nodejs.org/en/about/previous-releases#looking-for-latest-release-of-a-version-branch)
После установки, проверьте, появился ли npm на вашем компьютере. Выполните в терминале команду:
```
npm -v 
```

Находясь в директории проекта, установите зависимости и запустите проект в первом терминале:
```
npm i
npm run start
```
Cоздайте в директории /foodgram файл .env со следующими данными:
```
DB_NAME=foodgram                         # Название базы данных
DB_HOST=db                               # Имя хоста
DB_PORT=5432                             # Порт для соединения с базой данных
SECRET_KEY=ХХХ                           # Уникальный секретный ключ Django
ALLOWED_HOSTS=x.x.x.x,y,z                # Список хостов проекта, указывайте через запятую без пробелов и скобок
DEBUG=True                               # Режим отладки проекта Django активирован
USE_SQLITE=True                          # Режим работы с базой SQLite активирован
PROJECT_URL='https://janedomain.ru'      # Адрес вашего домена
```
Если хотите запустить проект локально с базой PostgreSQL, то добавьте в .env следующие переменные и измените USE_SQLITE на False:
```
USE_SQLITE=False                         # Режим работы с базой SQLite деактивирован
POSTGRES_DB=foodgram                     # Название базы данных
POSTGRES_USER=foodgram_user              # Имя пользователя базы данных
POSTGRES_PASSWORD=foodgram_password      # Пароль к базе данных
```
Запустите второй терминал, перейдите в нем в директорию проекта foodrgam/backend/:
```
cd foodgram/backend/
```
Создайте виртуальное окружение:
```
python -m venv venv
```
Установите зависимости проекта, выполните миграции:
```
python manage.py migrate
python manage.py runserver
```

Готово! По адресу [localhost:3000](localhost:3000) вы подняли локальную версию Foodgram, работающую на выбранной вами базе данных.


## ◑ Развернуть проект Foodgram на своем сервере с помощью Docker
### 1. Клонируйте репозиторий и перейдите в него в терминале:
```
git clone git@github.com:turbonyasha/foodgram.git
cd foodgram
```

### 2. Создайте Docker-образы и загрузите их на Dockerhub:
```
cd frontend
docker build -t <ваш_логин_на_докерхабе>/foodgram_frontend .
cd ../backend
docker build -t <ваш_логин_на_докерхабе>/foodgram_backend .
cd ../nginx
docker build -t <ваш_логин_на_докерхабе>/foodgram_gateway .

docker push <ваш_логин_на_докерхабе>/foodgram_frontend
docker push <ваш_логин_на_докерхабе>/foodgram_backend
docker push <ваш_логин_на_докерхабе>/foodgram_gateway
```


### 3. Задеплойте проект за свой сервер:
Подключитесь к своему серверу, создайте пустую директорию /foodgram и перейдите в нее
```
ssh -i путь_до_файла_с_SSH_ключом/название_файла_с_SSH_ключом имя_пользователя@ip_адрес_сервера
mkdir foodgram
cd foodgram
```
Установите на сервер docker-compose
```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin
```
В созданную директорию /foodgram скопируйте файл docker-compose.production.yml
```
scp -i путь_до_файла_с_SSH_ключом/название_файла_с_SSH_ключом docker-compose.production.yml имя_пользователя@ip_адрес_сервера:/home/username/foodgram/docker-compose.production.yml
```
Cоздайте в директории /foodgram файл .env со следующими данными:
```
sudo 

POSTGRES_DB=foodgram                     # Название базы данных
POSTGRES_USER=foodgram_user              # Имя пользователя базы данных
POSTGRES_PASSWORD=foodgram_password      # Пароль к базе данных
DB_NAME=foodgram                         # Название базы данных
DB_HOST=db                               # Имя хоста
DB_PORT=5432                             # Порт для соединения с базой данных
SECRET_KEY=ХХХ                           # Уникальный секретный ключ Django
ALLOWED_HOSTS=x.x.x.x,y,z                # Список хостов проекта, указывайте через запятую без пробелов и скобок
DEBUG=False                              # Режим отладки проекта Django деактивирован
USE_SQLITE=False                         # Режим работы с базой SQLite деактивирован
PROJECT_URL='https://janedomain.ru'      # Адрес вашего домена
```
Запустите docker compose в daemon-режиме:
```
sudo docker compose -f docker-compose.production.yml up -d
```
Выполните миграции и сбор статики в контейнере backend
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```
Отредактируйте конфигурацию Nginx на своем сервере для связи с портом контейнера Docker
```
sudo nano /etc/nginx/sites-enabled/default # откройте файл конфигурации

# измените настройки блока
location / {
    proxy_set_header Host $http_host;
    proxy_pass http://127.0.0.1:9000;
}
```
Проверьте файл конфигурации и перезапустите Nginx
```
sudo nginx -t
sudo service nginx reload
```

Все изображения пользователей и картинки рецептов, загружаемые пользователями, будут храниться в контейнере db в папке app/media.

Готово, вы развернули проект Foodgram на своем сервере и он полностью готов к вашим кулинарным изыскам!

## ◑ Настроить CI/CD Foodgram на GitHub Actions c DockerHUB
Проект предполагает автоматическое обновление Docker-образов на DockerHub, а также на вашем сервере после каждого пуша в любую ветку проекта. 
Каждое изменение в вашей версии проекта будет сразу же доступно вашим пользователям и вам ничего не потребуется для этого делать.

Готовый файл workflow уже находится в проекте в директории 
```
.github/workflows/main.yml
```
Перейтите в репозиторий проекта на GitHub, нажмите вкладку ***Settings***, в колонке слева выберите ***Secrets and variables***, в выпадающем меню выберите ***Actions*** и добавьте следующие секреты:
```
DOCKER_USERNAME           # имя пользователя на DockerHub
DOCKER_HUB_TOKEN          # ваш токен для Read, Write, Delete действий на DockerHub
SERVER_IP                 # IP своего сервера
SERVER_USER               # имя пользователя на вашем сервере
SSH_PRIVATE_KEY           # приватный SSH-ключ (id_rsa)
SERVER_SSH_PASSPHRASE     # кодовая фраза (пароль) для SSH-ключа
TELEGRAM_CHAT_ID          # ID вашего Telegram-аккаунта, куда будут приходить уведомления
TELEGRAM_BOT_TOKEN        # токен вашего бота в Telegram
```

Теперь каждое обновление, которое вы вносите в ваш проект, ваш сервер будет получать автоматически.

## ◑ Автор проекта
[Женя Скуратова]
- github [turbonyasha](https://github.com/turbonyasha)
- telegram [@janedoel](https://t.me/janedoel)

