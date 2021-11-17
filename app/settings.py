from flask import Blueprint, render_template
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from .db import db
from wtforms import SelectField, SubmitField
from wtforms.fields.html5 import IntegerField
from wtforms.widgets.html5 import NumberInput
from wtforms.validators import DataRequired, NumberRange
import pytz

blueprint = Blueprint('settings', __name__)


class SettingsForm(FlaskForm):
    timezone = SelectField(
        'Timezone', choices=list(map(lambda x: (x, x.replace("_", " ")), pytz.all_timezones)),
        validators=[
            DataRequired()
        ])

    start_of_day = IntegerField(
        'Start of day hour',
        widget=NumberInput(min=0, max=23),
        validators=[
            NumberRange(min=0, max=23)
        ]
    )

    submit = SubmitField('Save')


@blueprint.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm(obj=current_user)
    if form.validate_on_submit():
        current_user.timezone = form.timezone.data
        current_user.start_of_day = form.start_of_day.data
        db.session.commit()
        return render_template('settings.html', form=form, success=True)

    return render_template('settings.html', form=form)
