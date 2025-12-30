FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 1️⃣ Install system dependencies (CRITICAL)
RUN apt-get update && apt-get install -y \
    gcc \
    libgl1 \
    libglib2.0-0 \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# 2️⃣ Upgrade pip
RUN pip install --upgrade pip

# 3️⃣ Copy pyproject first (better caching)
COPY pyproject.toml ./

# 4️⃣ Install Python deps from pyproject.toml
RUN pip install .

# 5️⃣ Copy app code
COPY . .

# 6️⃣ Run app
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
