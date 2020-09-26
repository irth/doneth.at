from sqlalchemy.sql import func
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from datetime import datetime, timedelta
from .days import Day

db = SQLAlchemy()
migrate = Migrate()


def init_app(app):
    db.init_app(app)
    migrate.init_app(app, db)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    created_on = db.Column(db.DateTime, index=False, unique=False,
                           nullable=True, server_default=db.func.now())
    last_login = db.Column(db.DateTime, index=False, unique=False,
                           nullable=True)  # TODO: set on login? or remove?

    accomplishments = db.relationship(
        'Accomplishment', backref='user', lazy=True)

    # TODO: set user timezone from geoip on registration
    timezone = db.Column(db.String(64), nullable=False)
    start_of_day = db.Column(db.Integer, nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Accomplishment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_on = db.Column(db.DateTime, index=False, unique=False,
                           nullable=True, server_default=db.func.now())
    time = db.Column(db.DateTime(), nullable=False)
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
    def get_time_range(user, start: datetime, end: datetime):
        return Accomplishment.query.filter(
            Accomplishment.time >= start, Accomplishment.time < end, Accomplishment.user_id == user.id).all()

    @staticmethod
    def get_time_range_total(user, start: datetime, end: datetime):
        result = db.session.query(func.sum(Accomplishment.difficulty).label('total')).filter(
            Accomplishment.time >= start, Accomplishment.time < end, Accomplishment.user_id == user.id)[0][0]
        return result if result is not None else 0

    @staticmethod
    def get_day(user, day: Day):
        # TODO: allow setting custom "start of day" hour
        start = day.timestamp
        end = (day + 1).timestamp
        return Accomplishment.get_time_range(user, start, end)

    @staticmethod
    def get_day_total(user, day: Day):
        start = day.timestamp
        end = (day + 1).timestamp
        return Accomplishment.get_time_range_total(user, start, end)

    @staticmethod
    def get_today(user):
        today = Day.today(user)
        return Accomplishment.get_day(user, today)

    @staticmethod
    def get_today_total(user):
        today = Day.today(user)
        return Accomplishment.get_day_total(user, today)
