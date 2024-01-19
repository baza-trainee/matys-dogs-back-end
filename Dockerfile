# Use an official Python runtime as a parent image
FROM python:3.11

# Set metadata indicating the maintainer of the image
LABEL maintainer="jabsoluty@gmail.com"

# Set environment variables:
# PYTHONUNBUFFERED: Prevents Python from buffering stdout and stderr
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files to disk (optional, for performance)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libffi-dev \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*  # Clean up to reduce layer size

# Upgrade pip and install virtualenv for isolated Python environments
RUN pip install --upgrade pip \
    && pip install virtualenv

# Copy only the requirements file to install Python dependencies
# This is done before copying the whole project to leverage Docker cache layers
COPY requirements.txt ./

# Create and activate a virtual environment
RUN python -m virtualenv venv
ENV PATH="/app/venv/bin:$PATH"


# Install project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files into the container
COPY . .

RUN mkdir -p /vol/web/media
RUN mkdir -p /app/staticfiles

RUN adduser --disabled-password --no-create-home django-user && \
    chown -R django-user:django-user /vol/ && \
    chmod -R 755 /vol/web/
# Define the default command to run when starting the container
# Using gunicorn as the WSGI HTTP server
ENTRYPOINT ["gunicorn", "server_DJ.wsgi:application", "--bind", "0.0.0.0:8000"]

# Expose the port the app runs on
EXPOSE 8000
