FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# No CMD here — each service (moniter/api) will specify its own command
# via docker-compose.yml instead, since both share this same image.
