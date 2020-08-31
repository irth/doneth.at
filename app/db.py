from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from datetime import datetime, timedelta

from . import timeutils

db = SQLAlchemy()
migrate = Migrate()


def init_app(app):
    db.init_app(app)
    migrate.init_app(app, db)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    created_on = db.Column(db.DateTime, index=False,
                           unique=False, nullable=True)
    last_login = db.Column(db.DateTime, index=False,
                           unique=False, nullable=True)

    accomplishments = db.relationship(
        'Accomplishment', backref='user', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Accomplishment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    time = db.Column(db.DateTime(), nullable=False,
                     default=db.func.current_timestamp())
    text = db.Column(db.String(256), nullable=False)
    difficulty = db.Column(db.Integer)

    @property
    def difficulty_class(self):
        if self.difficulty < 0:
            return "negative"
        if self.difficulty == 0:
            return "zero"
        if self.difficulty <= 5:
            return "easy"
        if self.difficulty <= 10:
            return "medium"
        return "hard"

    @staticmethod
    def get_time_range(user_id, start, end):
        return Accomplishment.query.filter(
            Accomplishment.time >= start, Accomplishment.time < end, Accomplishment.user_id == user_id).all()

    @staticmethod
    def get_day(user_id, day):
        # TODO: allow setting custom "start of day" hour
        start = timeutils.day(day)
        end = timeutils.day_after(day)
        return Accomplishment.get_time_range(user_id, start, end)

    @staticmethod
    def get_today(user_id):
        today = datetime.now()
        return Accomplishment.get_day(user_id, today)
