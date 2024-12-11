import logging
from app import create_app, db
from app.config import DevelopmentConfig, ProductionConfig
from app.logger import setup_logging

# Set up logging first
setup_logging()

# Create the app instance
app = create_app()

# Choose configuration based on environment variable FLASK_ENV
env = app.config.get("ENV", "development")  # Default to 'development' if 'ENV' is missing
if env == "production":
    app.config.from_object(ProductionConfig)
else:
    app.config.from_object(DevelopmentConfig)

# Initialize the app context
with app.app_context():
    try:
        # Database creation or migration logic here
        db.create_all()
        app.logger.info("Database and tables created successfully.")
    except Exception as e:
        app.logger.error(f"Error creating database: {e}")

# Run the app with the appropriate settings
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=app.config['DEBUG'])  # Use app.config['DEBUG'] instead of hardcoding
