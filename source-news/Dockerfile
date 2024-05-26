FROM python:3.11

WORKDIR /app

RUN apt-get update

COPY requirements.txt .
RUN pip install -U --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "scrape.py"]
