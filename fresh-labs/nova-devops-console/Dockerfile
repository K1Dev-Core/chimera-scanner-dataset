FROM python:3.12-slim

WORKDIR /srv/nova

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl iputils-ping procps \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY static ./static
COPY seed ./seed
COPY flag.txt /flag.txt

ENV PYTHONUNBUFFERED=1
ENV NOVA_ENV=production

EXPOSE 8080

CMD ["python", "app.py"]
