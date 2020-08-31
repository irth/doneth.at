from flask import Blueprint, render_template
from .db import db, Accomplishment, User

blueprint = Blueprint('stats', __name__)


@blueprint.route('/stats')
def stats():
    total_accomplishments = Accomplishment.query.count()
    total_accomplishments_by_me = Accomplishment.query.filter_by(
        user_id=1).count()
    total_users = User.query.count()

    return render_template(
        'stats.html',
        total=total_accomplishments,
        total_without_mine=total_accomplishments - total_accomplishments_by_me,
        total_users=total_users
    )
