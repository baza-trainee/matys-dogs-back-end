# Создание Dockerfile в корне проекта
# Установка базового образа
FROM python:3.11

# Установка рабочей директории внутри контейнера
WORKDIR /app

# Копирование requirements.txt внутрь контейнера
COPY requirements.txt /app

# Установка зависимостей
RUN pip install -r requirements.txt

# Копирование всех файлов из текущего каталога внутрь контейнера
COPY . /app