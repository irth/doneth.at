from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "raleicuu0Engohh3iageephoh3looge0okupha2omeiph7Nooyeey1tiewooxu7phaeshi0ohlaaThai2eth1oapong5iroo4fieleekaidohmoh1eYahjei9Yi6aema"

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    return app
