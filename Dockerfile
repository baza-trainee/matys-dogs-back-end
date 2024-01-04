FROM python:3.11

# Установка рабочей директории внутри контейнера
WORKDIR /app

# Install system dependencies, including libcairo2
RUN apt-get update && apt-get install -y libffi-dev libcairo2

# Upgrade pip
RUN pip install --upgrade pip
# Копирование requirements.txt внутрь контейнера
COPY requirements.txt /app/

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всех файлов из текущего каталога внутрь контейнера
COPY . /app/

ENTRYPOINT ["gunicorn", "server_DJ.wsgi:application", "-b", "0.0.0.0:8000"]
