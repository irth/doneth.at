from . import timeutils
from flask import Blueprint, render_template, redirect, url_for, abort
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from .db import db, Accomplishment
from datetime import datetime, timedelta

main = Blueprint('main', __name__)


class NewAccomplishementForm(FlaskForm):
    text = StringField(
        'Accomplishment',
        validators=[
            DataRequired(), Length(max=256)])
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


def get_day_template_data(day_string):
    day_datetime = None
    if day_string == "today":
        day_datetime = timeutils.today()
    else:
        day_datetime = timeutils.from_str(day_string)

    day_string_clean = timeutils.as_str(day_datetime)

    accomplishments = list(reversed(
        Accomplishment.get_day(current_user.id, day_datetime)))
    total = sum(a.difficulty for a in accomplishments)

    yesterday = timeutils.day_before(day_datetime)
    tomorrow = timeutils.day_after(day_datetime)
    if timeutils.is_future(tomorrow):
        tomorrow = None

    return {
        "day": {
            "datetime": day_datetime,
            "string": day_string_clean,
            "fancy": timeutils.as_fancy_str(day_datetime),
            "is_today": timeutils.is_today(day_datetime)
        },

        "links": {
            "yesterday": url_for('main.index', day=timeutils.as_str(yesterday)),
            "tomorrow": url_for('main.index', day=timeutils.as_str(tomorrow)) if tomorrow is not None else None
        },

        "accomplishments": accomplishments,
        "total_xp": sum(a.difficulty for a in accomplishments),
    }


@main.route('/', defaults={'day': 'today'}, methods=['GET', 'POST'])
@main.route('/day/<day>')
def index(day):
    if not current_user.is_authenticated:
        return render_template('index.html')

    form = NewAccomplishementForm()
    if form.validate_on_submit():
        return handle_accomplishment_submission(form)

    return render_template(
        'main/app.html',
        form=form,
        **get_day_template_data(day)
    )


@main.route('/day/<day>/edit')
@login_required
def edit_day(day):
    form = NewAccomplishementForm()
    if form.validate_on_submit():
        return handle_accomplishment_submission(form)

    return render_template(
        'main/app.html',
        form=form,
        edit=True,
        **get_day_template_data(day)
    )


class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')


@main.route('/accomplishment/<accomplishment_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_accomplishment(accomplishment_id):
    a = Accomplishment.query.get_or_404(accomplishment_id)
    if a.user_id != current_user.id:
        abort(403)

    back_url = url_for(
        'main.edit_day', day=timeutils.as_str(timeutils.day(a.time)))

    form = DeleteForm()
    if form.validate_on_submit():
        db.session.delete(a)
        db.session.commit()
        return redirect(back_url)

    return render_template(
        'main/delete.html',
        form=form,
        accomplishment=a,
        cancel=back_url)
