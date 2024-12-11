import logging
from app import create_app, db
from app.logger import setup_logging

# Set up logging first
setup_logging()

# Create the app instance
app = create_app()


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
