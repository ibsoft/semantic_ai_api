import importlib
import logging
from elasticsearch import Elasticsearch
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from redis import Redis
from .config import Config

logger = logging.getLogger()

db = SQLAlchemy()
jwt = JWTManager()

redis_client = Redis.from_url(Config.REDIS_URL)

# Import the utils module
utils_module = "app.utils"  # Single utils module
try:
    utils = importlib.import_module(utils_module)  # Import the merged utils
    logger.info(f"Successfully imported {utils_module}")
except ModuleNotFoundError as e:
    logger.error(f"Error importing {utils_module}: {e}")
    raise ImportError(f"Module {utils_module} could not be found")

# Initialize Elasticsearch client
try:
    es = Elasticsearch(Config.ELASTICSEARCH_URL)
    if es.ping():
        logger.info("Successfully connected to Elasticsearch")
    else:
        logger.warning("Failed to connect to Elasticsearch")
except Exception as e:
    logger.error(f"Error connecting to Elasticsearch: {e}")
    raise ConnectionError(f"Could not connect to Elasticsearch at {Config.ELASTICSEARCH_URL}")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    from .api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
