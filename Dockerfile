FROM python:3-slim-buster

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DATABASE_URL sqlite:////data/app.db
COPY ./requirements.txt /app/requirements.txt
RUN apt-get update && \
    apt-get install -y gosu && \
    rm -rf /var/lib/apt/lists/* && \
    pip install -r requirements.txt && pip install gunicorn
COPY . /app/
RUN flask digest compile
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"]
