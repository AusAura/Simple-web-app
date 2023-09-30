FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 3000

VOLUME [ "/Storage" ]

CMD ["python", "main.py"]