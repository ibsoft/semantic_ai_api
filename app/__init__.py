import importlib
import logging
from elasticsearch import Elasticsearch
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from flask_jwt_extended import JWTManager
from redis import Redis
from app.config import Config
from app.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize core components
db = SQLAlchemy()
jwt = JWTManager()
redis_client = Redis.from_url(Config.REDIS_URL)

# Import the utils module dynamically
utils_module = "app.utils"
try:
    utils = importlib.import_module(utils_module)
    logger.info(f"Successfully imported {utils_module}")
except ModuleNotFoundError as e:
    logger.error(f"Error importing {utils_module}: {e}")
    raise ImportError(f"Module {utils_module} could not be found.")

# Initialize Elasticsearch client
try:
    es = Elasticsearch(Config.ELASTICSEARCH_URL)
    if es.ping():
        logger.info("Successfully connected to Elasticsearch.")
    else:
        logger.warning("Failed to connect to Elasticsearch.")
except Exception as e:
    logger.error(f"Error connecting to Elasticsearch: {e}")
    raise ConnectionError(f"Could not connect to Elasticsearch at {Config.ELASTICSEARCH_URL}.")

# Define application factory
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    
    with app.app_context():
        try:
            # Use Inspector to check for existing tables
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if not existing_tables:  # If no tables exist, create them
                db.create_all()
                logger.info("Database and tables created successfully.")              
            else:
                logger.info("Database tables already exist. Skipping creation.")
            
                           # Ensure Elasticsearch index is set up
                def create_index_with_mapping(index_name="skl_categories_index"):
                    """
                    Create Elasticsearch index with the necessary mapping for vector search.
                    """
                    mapping = {
                    "mappings": {
                        "properties": {
                            "SUPERCATEGORY": {"type": "text"},
                            "CATEGORY": {"type": "text"},
                            "CATEGORY_CODE": {"type": "keyword"},
                            "SUBCATEGORY": {"type": "text"},
                            "SUBCATEGORY_CODE": {"type": "keyword"},
                            "SIGNIFICANCE": {"type": "keyword"},
                            "TCID": {"type": "integer"},
                            "embedding": {"type": "dense_vector", "dims": 768},
                        }
                    }
                }

                    
                

                    if not es.indices.exists(index=index_name):
                        es.indices.create(index=index_name, body=mapping)
                        logger.info(f"Index '{index_name}' created successfully.")
                    else:
                        logger.info(f"Index '{index_name}' already exists.")

                create_index_with_mapping()
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    # Register Blueprints
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1/')
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"msg": "Internal Server Error"}), 500

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"msg": "Not Found"}), 404
    
    return app
