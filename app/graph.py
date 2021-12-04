from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .db import db, Accomplishment
from .days import Day

blueprint = Blueprint('graph', __name__)


@blueprint.route('/graph.svg')
@login_required
def graph_svg():
    count = 7
    accomplishments = [0]*count
    days = [""]*count
    day = Day.today(current_user)

    for i in range(1, count+1):
        total_xp = Accomplishment.get_day_total(current_user, day)
        accomplishments[-i] = total_xp
        days[-i] = day.timestamp.strftime('%a')[:2]
        day -= 1

    return render_template('graph.svg', days=days, **gen_graph_data(accomplishments)), 200, {'Content-Type': 'image/svg+xml', 'Cache-Control': 'no-cache'}


def gen_scale(base=10):
    return [base*i for i in range(0, 5)]


def find_scale_base(max_n):
    if max_n < 20:
        return 10

    return (max_n - (max_n - 1) % 20 + 20) // 4
    n = max_n % 20
    while n % 20 != 0:
        n += 1
    return n//4


GRAPH_TOP_LINE = 16.6
GRAPH_BOTTOM_LINE = 83

GRAPH_RANGE = GRAPH_BOTTOM_LINE - GRAPH_TOP_LINE


def absolute_to_percentage_position(n, scale_base):
    scale_top = scale_base * 4
    return round(GRAPH_BOTTOM_LINE - n/scale_top * GRAPH_RANGE, 2)


def gen_graph_data(numbers):
    assert len(numbers) > 1
    max_n = max(numbers)
    scale_base = find_scale_base(max_n)
    scale = gen_scale(scale_base)

    dots = [absolute_to_percentage_position(
        n, scale_base) for n in numbers]
    lines = list(zip(dots, dots[1:]))
    avg = sum(dots)/len(dots)
    print(dots)
    print(avg)

    return {
        "dots": dots,
        "lines": lines,
        "scale": scale,
        "avg": avg,
    }
