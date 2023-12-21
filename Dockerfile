# Создание Dockerfile в корне проекта
# Установка базового образа
FROM python:3.11

# Установка рабочей директории внутри контейнера
WORKDIR /app

RUN apt-get update

RUN pip install --upgrade pip
# Копирование requirements.txt внутрь контейнера
COPY requirements.txt /app

# Установка зависимостей
RUN pip install -r requirements.txt

# Копирование всех файлов из текущего каталога внутрь контейнера
COPY . /app

ENTRYPOINT ["gunicorn", "server_DJ.wsgi:application", "-b", "0.0.0.0:8000"]
