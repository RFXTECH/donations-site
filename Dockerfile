FROM python:3.11-slim

ARG APP_VERSION=dev
ARG BUILD_SHA=unknown
ARG BUILD_TIME=unknown

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATA_DIR=/data \
    APP_VERSION=${APP_VERSION} \
    BUILD_SHA=${BUILD_SHA} \
    BUILD_TIME=${BUILD_TIME}

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY app.py .

EXPOSE 8080

CMD ["python", "app.py"]
