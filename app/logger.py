import logging
from flask import request
from app.config import Config 

class RequestFormatter(logging.Formatter):
    def format(self, record):
        # Try to get the client's IP address
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr) if request else "SEMANTIC-CATEGORIES-API"
        # Prepend the IP address to the log message
        record.client_ip = client_ip
        return super().format(record)

def setup_logging():
    # Log setup
    logging.basicConfig(
        level=Config.LOG_LEVEL,
        handlers=[
            logging.FileHandler('logs/app.log', encoding='utf-8'),  # File handler
            logging.StreamHandler()  # Stream handler
        ]
    )

    # Create and apply the custom formatter
    formatter = RequestFormatter('%(client_ip)s - %(asctime)s - %(levelname)s - %(message)s')

    # Apply the formatter to all handlers
    for handler in logging.getLogger().handlers:
        handler.setFormatter(formatter)

