from flask import Blueprint, render_template, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from flask_login import LoginManager, login_user, logout_user
import sqlalchemy.exc
from .db import db, User

blueprint = Blueprint('auth', __name__)
login_manager = LoginManager()


def init_app(app):
    login_manager.init_app(app)


@login_manager.user_loader
def loader(id):
    return User.query.filter_by(id=id).first()


class SignupForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=2), Length(max=64)]
    )
    password = PasswordField(
        'Password',
        validators=[
            Length(
                min=8, message='The password needs to be at least 8 characters long'),
            DataRequired()
        ]
    )
    confirm = PasswordField(
        'Confirm password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords do not match')
        ]
    )
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired()]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )
    submit = SubmitField('Log in')


class LogoutForm(FlaskForm):
    submit = SubmitField('Log out')


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = SignupForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            db.session.rollback()
            if "UNIQUE" in str(e):
                form.username.errors.append('Username already taken.')
                return render_template('auth/register.html', form=form)
            else:
                raise
        login_user(user)
        return redirect('/')
    return render_template('auth/register.html', form=form)


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=True)
            return redirect('/')
        else:
            form.password.errors.append('Invalid username or password.')
            return render_template('auth/login.html', form=form)

        return redirect('/')
    return render_template('auth/login.html', form=form)


@blueprint.route('/logout', methods=['GET', 'POST'])
def logout():
    form = LogoutForm()
    if form.validate_on_submit():
        logout_user()
        return redirect('/')
    return render_template('auth/logout.html', form=form)
