from . import timeutils
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from .db import db, Accomplishment
from datetime import datetime, timedelta

main = Blueprint('main', __name__)


class NewAccomplishementForm(FlaskForm):
    text = StringField('Accomplishment', validators=[
                       DataRequired(), Length(max=128)])
    submit_5 = SubmitField('5 XP')
    submit_10 = SubmitField('10 XP')
    submit_15 = SubmitField('15 XP')


def handle_accomplishment_submission(form):
    accomplishment = Accomplishment()
    accomplishment.user_id = current_user.id
    accomplishment.text = form.text.data
    accomplishment.difficulty = 5
    if form.submit_10.data:
        accomplishment.difficulty = 10
    elif form.submit_15.data:
        accomplishment.difficulty = 15
    # the timestamp should be set by the database
    db.session.add(accomplishment)
    db.session.commit()
    return redirect(url_for('main.index'))


@main.route('/', defaults={'day': 'today'}, methods=['GET', 'POST'])
@main.route('/day/<day>')
def index(day):
    day_datetime = None
    day_string = None
    is_today = False
    if day == "today":
        day_datetime = timeutils.today()
        day_string = "Today"
        is_today = True
    else:
        day_datetime = timeutils.from_str(day)
        if timeutils.is_today(day_datetime):
            return redirect('/')
        day_string = timeutils.as_fancy_str(day_datetime)

    if not current_user.is_authenticated:
        return render_template('index.html')

    form = NewAccomplishementForm()
    if form.validate_on_submit():
        return handle_accomplishment_submission(form)

    accomplishments = list(reversed(Accomplishment.get_day(
        current_user.id, day_datetime)))
    total = sum(a.difficulty for a in accomplishments)

    tomorrow = timeutils.day_after(day_datetime)
    yesterday = timeutils.day_before(day_datetime)

    if timeutils.is_future(tomorrow):
        tomorrow = None

    return render_template(
        'main/app.html',
        form=form,
        day=day_string,
        accomplishments=accomplishments,
        total=total,
        tomorrow=timeutils.as_str(tomorrow),
        yesterday=timeutils.as_str(yesterday),
        is_today=is_today,
    )
