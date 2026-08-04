FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends iputils-ping \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY static ./static
COPY reports ./reports

ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["python", "app.py"]
