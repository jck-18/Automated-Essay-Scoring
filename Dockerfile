FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything else
COPY . .

# Create model directory
RUN mkdir -p bert_multiclass_model

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV ENABLE_API=True

# Expose ports for Streamlit and FastAPI
EXPOSE 8000
EXPOSE 8501

# Use the run script as entrypoint
ENTRYPOINT ["python", "run.py"]

# Default to running both servers
CMD ["--mode", "both"] 