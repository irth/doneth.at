import os
from flask import Flask

from flask_static_digest import FlaskStaticDigest
flask_static_digest = FlaskStaticDigest()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv(
        "FLASK_SECRET_KEY", "raleicuu0Engohh3iageephoh3looge0okupha2omeiph7Nooyeey1tiewooxu7phaeshi0ohlaaThai2eth1oapong5iroo4fieleekaidohmoh1eYahjei9Yi6aema")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        "DATABASE_URL", "sqlite:///app.db")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    flask_static_digest.init_app(app)

    from . import db
    db.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from . import auth
    auth.init_app(app)
    app.register_blueprint(auth.blueprint)

    from . import stats
    app.register_blueprint(stats.blueprint)

    return app
