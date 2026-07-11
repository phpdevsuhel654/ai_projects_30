from flask import Flask

from config import Config
from database.db import init_db
from routes.home_routes import home_bp
from routes.prediction_routes import prediction_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(home_bp)
    app.register_blueprint(prediction_bp)

    with app.app_context():
        init_db()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=5000)
