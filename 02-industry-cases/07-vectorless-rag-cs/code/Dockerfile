FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for PyMuPDF + RapidOCR + git
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    gcc \
    libglib2.0-0 \
    libgl1 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Clone PageIndex (MIT license · Vectify AI) — Vectorless RAG 核心库
RUN git clone --depth 1 https://github.com/VectifyAI/PageIndex.git \
    && pip install --no-cache-dir -r PageIndex/requirements.txt

# Copy application code
COPY . .

# Create runtime data directories
RUN mkdir -p app/indexes app/knowledge data

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
