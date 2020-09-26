from flask import Blueprint, render_template, redirect, url_for, abort, request
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange
from .db import db, Accomplishment
from datetime import datetime, timedelta
import time
from .days import Day

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
    accomplishment.time = Day.today(current_user).timestamp
    db.session.add(accomplishment)
    db.session.commit()
    return redirect(url_for('main.index'))


def parse_day(day_string, user):
    day = None
    if day_string == "today":
        day = Day.today(user)
    else:
        day = Day.from_str(day_string, user)

    return day


def get_day_template_data(day_string, user):
    day = parse_day(day_string, user)

    accomplishments = list(reversed(
        Accomplishment.get_day(current_user, day)))
    total = sum(a.difficulty for a in accomplishments)

    yesterday = day - 1
    tomorrow = day + 1
    if tomorrow.is_future:
        tomorrow = None

    return {
        "day": day,
        "links": {
            "yesterday": url_for('main.index', day=yesterday.url),
            "tomorrow": url_for('main.index', day=tomorrow.url) if tomorrow is not None else None
        },
        "accomplishments": accomplishments,
        "total_xp": sum(a.difficulty for a in accomplishments),
        "ts": int(time.time()),  # timestamp for cachebusting
    }


@main.route('/', defaults={'day': 'today'}, methods=['GET', 'POST'])
@main.route('/day/<day>')
def index(day):
    if not current_user.is_authenticated:
        # TODO: handle the case when the user is on /day/<something> and is not logged in
        return render_template('index.html')

    form = NewAccomplishementForm()
    if form.validate_on_submit():
        return handle_accomplishment_submission(form)

    return render_template(
        'main/app.html',
        form=form,
        **get_day_template_data(day, current_user)
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
        **get_day_template_data(day, current_user)
    )


class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')


@main.route('/accomplishment/<accomplishment_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_accomplishment(accomplishment_id):
    a = Accomplishment.query.get_or_404(accomplishment_id)
    if a.user_id != current_user.id:
        abort(403)

    back_url = url_for('main.edit_day', day=Day.from_timestamp(
        a.time, current_user).url)

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


class EditForm(FlaskForm):
    text = StringField(
        'Accomplishment',
        validators=[DataRequired(), Length(max=256)]
    )
    difficulty = IntegerField(
        'Difficulty (XP)',
        validators=[DataRequired(), NumberRange(max=100, min=-100)]
    )
    submit = SubmitField('Save')


@main.route('/accomplishment/<accomplishment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_accomplishment(accomplishment_id):
    a = Accomplishment.query.get_or_404(accomplishment_id)
    if a.user_id != current_user.id:
        abort(403)

    back_url = url_for('main.edit_day', day=Day.from_timestamp(
        a.time, current_user).url)

    form = EditForm(obj=a)
    if form.validate_on_submit():
        a.text = form.text.data
        a.difficulty = form.difficulty.data
        db.session.commit()
        return redirect(back_url)

    return render_template('main/edit.html', form=form, cancel=back_url)


@main.route('/day/<day>/add', methods=['GET', 'POST'])
@login_required
def add_day(day):
    day = parse_day(day, current_user)
    form = EditForm()

    back_url = ""

    from_top = ("from" in request.args) and ("top" in request.args["from"])
    # to the bottom
    # bottom to top I stop
    # at the core I've forgotten
    # in the middle of my thoughts
    # taken far from my safety
    # the picture is there
    back_to_day = url_for('main.index', day=day.url)
    back_to_edit = url_for('main.edit_day', day=day.url)

    if form.validate_on_submit():
        accomplishment = Accomplishment()
        accomplishment.user_id = current_user.id
        accomplishment.text = form.text.data
        accomplishment.difficulty = form.difficulty.data
        accomplishment.time = day.timestamp
        db.session.add(accomplishment)
        db.session.commit()
        return redirect(back_to_day)

    return render_template(
        'main/edit.html',
        day=day,
        form=form,
        edit=True,
        cancel=back_to_day if from_top else back_to_edit
    )
