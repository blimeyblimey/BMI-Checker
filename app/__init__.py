import logging
from flask import Flask
from app.config import Config

def create_app(config_class=Config):
    # Configure production-ready logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    app = Flask(__name__)
    app.config.from_object(config_class)

    from app.routes import bp
    app.register_blueprint(bp)

    return app