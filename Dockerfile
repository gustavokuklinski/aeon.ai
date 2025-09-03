FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY plugins/ ./plugins/

RUN pip install --no-cache-dir -r requirements.txt

RUN for d in plugins/*; do \
    if [ -f "$d/requirements.txt" ]; then \
        pip install --no-cache-dir -r "$d/requirements.txt"; \
    fi; \
    done

EXPOSE 4303

CMD ["python", "aeon.py"]