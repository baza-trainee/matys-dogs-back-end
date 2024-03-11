FROM nginx:latest

# Копирование конфигурационного файла nginx
COPY nginx.conf /etc/nginx/nginx.conf

RUN addgroup --system nginxuser && adduser --system --no-create-home --ingroup nginxuser nginxuser
USER nginxuser

# Add a health check for the nginx service
# This example uses `curl` to perform the health check. Ensure `curl` is installed in your base image or add it.
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl --fail http://localhost:80/ || exit 1