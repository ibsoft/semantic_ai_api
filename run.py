import logging
from app import create_app, db
from app.config import Config
from app.logger import setup_logging

setup_logging()

logger = logging.getLogger()

app = create_app()



with app.app_context():
    try:
        db.create_all()
        logger.info("Database and tables created successfully.")
    except Exception as e:
        print(f"Error creating database: {e}")

if __name__ == "__main__" :
    app.run()
    

    
