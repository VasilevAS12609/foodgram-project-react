# Дипломный проект - FoodGram «Продуктовый помощник»

![Workflow Status](https://github.com/VasilevAS12609/foodgram-project-react/actions/workflows/main.yml/badge.svg)

## Описание проекта:
## FoodGram - «Продуктовый помощник»

Это онлайн-сервис, реализованный посредствам API, на котором пользователи могут публиковать рецепты, подписываться на других пользователей, добавлять рецепты в «Избранное», и скачивать сводный список продуктов, необходимых для приготовления выбранных блюд.

## Запуск проекта с помощью Docker

1. Клонируем репозиторий:

    ```
    git clone git@github.com:VasilevAS12609/foodgram-project-react.git
    ```

2. Создаем файл .env с переменными окружения, необходимыми для работы приложения:

    ```
   SECRET_KEY='XxX'
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=postgres
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=password
   DB_HOST=db
   DB_PORT=5432
    ```

3. Переходим в директорию infra/ и выполняем команду для создания и запуска контейнеров:
    ```
    sudo docker compose up -d --build
    ```

4. В контейнере backend выполняем миграции, создаем суперпользователя и собераем статику:

    ```
    sudo docker compose exec web python manage.py migrate
    sudo docker compose exec web python manage.py createsuperuser
    sudo docker compose exec web python manage.py collectstatic --no-input 
    ```

5. Загружаем в бд ингредиенты командой ниже:

    ```
    sudo docker compose exec web python manage.py importdb
    ```

6. Проект будет доступен по следующим адресам:
    -  http://localhost/admin/ - админ панель;
    -  http://localhost/api/ - API проекта
    -  http://localhost/api/docs/redoc.html - документация к API

## Запуск проекта на сервере:

Отредактируйте файл `infra/default.conf` и в строке `server_name` впишите IP виртуальной машины (сервера).  
Скопируйте папку `infra` из вашего проекта на сервер в home/<ваш_username>/.

Установите Docker и Docker-compose на сервере:
```
sudo apt install docker.io
sudo apt install docker-compose
```

---
### Автор проекта:
**[Алексей Васильев](https://github.com/VasilevAS12609)**
### Информация для ревью:
Боевой сервер - **[http://vasilevdev.ddns.net/](http://vasilevdev.ddns.net/)**

Данные админки:
 - почта: vasilevas12609@gmail.com
 - пароль: YPTest2022