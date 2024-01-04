# Создание Dockerfile в корне проекта
# Установка базового образа
FROM python:3.11

# Установка рабочей директории внутри контейнера
WORKDIR /app

RUN apt-get update && apt-get install -y libffi-dev libcairo2

# Set an environment variable for cairocffi
ENV CAIROCFFI_VERSION=1.3.0
# Install system dependencies, including libcairo2

RUN pip install --upgrade pip

# Копирование requirements.txt внутрь контейнера
COPY requirements.txt /app

# Установка зависимостей
RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir

# Копирование всех файлов из текущего каталога внутрь контейнера
COPY . /app

ENTRYPOINT ["gunicorn", "server_DJ.wsgi:application", "-b", "0.0.0.0:8000"]
