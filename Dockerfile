# -------- Builder stage --------
FROM python:3.11-slim AS builder

WORKDIR /app

# Cache transformers models in a temp folder
ENV TRANSFORMERS_CACHE=/tmp/huggingface
ENV HF_HOME=/tmp/huggingface

COPY requirements.txt .

# Upgrade pip, install dependencies without caching
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache

# Install CPU-only PyTorch explicitly
RUN pip install --no-cache-dir torch==2.9.1+cpu --index-url https://download.pytorch.org/whl/cpu

# -------- Runtime stage --------
FROM python:3.11-slim

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local /usr/local

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

