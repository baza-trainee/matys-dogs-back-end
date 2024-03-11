FROM python:3.11


LABEL maintainer="jabsoluty@gmail.com"


ENV PORT=8000 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1


WORKDIR /app

RUN apt-get update && apt-get install -y \
    libffi-dev \
    libcairo2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*



RUN python -m venv venv
ENV PATH="/app/venv/bin:$PATH"


COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


COPY . .

RUN mkdir -p /app/staticfiles
VOLUME ["/app/media", "/vol/web/media"]

EXPOSE 8000

ENTRYPOINT ["gunicorn", "server_DJ.wsgi:application", "--bind", "0.0.0.0:8000"]


