FROM python:3.11-slim

WORKDIR /app

# System dependencies install karo
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies install karo
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bot files copy karo
COPY . .

# Bot start karo
CMD ["python", "bot.py"]
