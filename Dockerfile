# Use a lightweight Python base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies if any are needed for Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements files first to leverage Docker's cache
COPY requirements.txt .
COPY plugins/ ./plugins/

RUN pip install --no-cache-dir -r requirements.txt

RUN for d in plugins/*; do \
    if [ -f "$d/requirements.txt" ]; then \
        pip install --no-cache-dir -r "$d/requirements.txt"; \
    fi; \
    done

EXPOSE 4303

ENTRYPOINT ["python", "aeon.py"]

CMD ["--terminal"]