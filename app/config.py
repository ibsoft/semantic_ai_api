import os

class Config:
    # Secret key for JWT
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
    JWT_EXPIRATION = int(os.getenv("JWT_EXPIRATION", 3600))  # 1 hour, configurable
    RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", 10000))  # Max requests per time window
    RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", 60))  # 1 minute default

    # API Keys for OpenAI and Ollama
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/embeddings")
    OLLAMA_MODEL = "paraphrase-multilingual"
    MODEL = os.getenv("MODEL", "gpt-4o-mini")  # GPT model ID or name

    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "app.log")  # Log file, defaults to 'app.log'

    # Redis Configuration
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    USE_REDIS = os.getenv("USE_REDIS", "False").lower() in ["true", "1", "t", "y", "yes"]
    REDIS_CACHE_EXPIRATION = int(os.getenv("REDIS_CACHE_EXPIRATION", 3600))  # Cache expiration in seconds

    # SQLAlchemy Configuration (Database)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", f"sqlite:///{os.path.join(BASE_DIR, 'database/app.db')}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Elasticsearch Configuration
    ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")

    # General Settings
    USE_EXAMPLES = os.getenv("USE_EXAMPLES", "True").lower() in ["true", "1", "t", "y", "yes"]
    EXAMPLES_SIMILARITY_THRESHOLD = float(os.getenv("EXAMPLES_SIMILARITY_THRESHOLD", 0.8))  # Similarity threshold for examples

# Environment-specific configuration
class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:")  # In-memory DB for development

class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = "ERROR"  # Set to error level in production
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "postgres://user:password@localhost/prod_db")

# Select configuration based on the environment
config_class = DevelopmentConfig if os.getenv("FLASK_ENV") == "development" else ProductionConfig
