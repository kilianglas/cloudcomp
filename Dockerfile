FROM continuumio/miniconda3

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 80

ENTRYPOINT [ "python" ]

CMD [ "main.py" ]