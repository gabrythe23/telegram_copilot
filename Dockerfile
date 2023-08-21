FROM python:3.9

RUN pip install telethon openai

COPY . /app/

CMD [ "python", "/app/main.py" ]
