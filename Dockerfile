FROM node:current-alpine
COPY . /app/
WORKDIR /app
ENV NODE_ENV=production
RUN yarn install && yarn build && rm -rf node_modules


FROM python:3-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DATABASE_URL sqlite:////data/app.db
ENV FLASK_APP app
ENV FLASK_DEBUG 0
COPY ./requirements.txt /requirements.txt
RUN apt-get update && \
    apt-get install -y gosu && \
    rm -rf /var/lib/apt/lists/* && \
    pip install -r /requirements.txt && pip install gunicorn
COPY --from=0 /app/ /app
WORKDIR /app
RUN flask digest compile
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"]
