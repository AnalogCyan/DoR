FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 53/udp
EXPOSE 53/tcp

VOLUME /app/cache

CMD ["python", "server.py"]
