FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py ip_generator.py ./

EXPOSE 53/udp
CMD [ "python", "server.py" ]
