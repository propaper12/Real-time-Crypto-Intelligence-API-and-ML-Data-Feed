FROM python:3.10-slim

WORKDIR /app

# Install dependencies first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all code (includes handlers/, workers/, formatters/ sub-packages)
COPY . .

# Run the aiogram bot as a microservice
CMD ["python", "-u", "bot.py"]
