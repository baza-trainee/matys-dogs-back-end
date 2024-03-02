# Maty's Dogs Back-End

This project serves as the backend for Maty's Dogs, utilizing Django as the core framework, along with Docker for containerization and PostgreSQL for database management.

## Core Technologies

- **Django**: Used as the main web framework for building the back-end.
- **Docker**: Utilized for containerizing the application, ensuring consistent environments across different stages of development.
- **PostgreSQL**: The preferred database for storing application data, configured within the Docker setup.
- **Gunicorn**: Chosen as the WSGI HTTP Server to run Django, facilitating better concurrency and management of requests.

## Additional Libraries and Tools

- **Django REST framework**: For building powerful and flexible APIs.
- **Django Allauth**: For authentication mechanisms.
- **Django CORS Headers**: To handle Cross-Origin Resource Sharing.
- **Psycopg2**: PostgreSQL database adapter for Python.
- **Pillow**: For image processing capabilities within Django.
- **Whitenoise**: To serve static files directly from Django without requiring a separate web server.

## Installation

To get the project up and running on your local machine, follow these steps:

1. **Clone the repository:**

```bash
git clone https://github.com/IOabsolutes/matys-dogs-back-end.git
cd matys-dogs-back-end
```

2. **Set up the Docker environment:**

Ensure you have Docker and Docker Compose installed on your system. Then, build and run the containers:

```bash
docker-compose up --build
```

This command will set up the entire environment, including the Django server, PostgreSQL database, and any other services defined in `docker-compose.yml`.

3. **Access the application:**

Once the containers are up, you can access the backend services as defined in the project's `docker-compose.yml` and Django `urls.py`.

