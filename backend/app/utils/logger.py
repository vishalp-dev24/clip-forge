import logging
import os
from config.paths import RUNTIME_LOGS_API

# Sets up the logging configuration for the application.
def setup_logging():
    # Create the directory for the log files if it doesn't already exist.
    os.makedirs(os.path.dirname(RUNTIME_LOGS_API), exist_ok=True)
    # Configure the basic logging settings.
    logging.basicConfig(
        # Set the minimum level of messages to log.
        level=logging.INFO,
        # Define the format of the log messages.
        format="%(asctime)s [%(levelname)s] %(message)s",
        # Specify the handlers to use for logging.
        handlers=[
            # Log messages to a file.
            logging.FileHandler(RUNTIME_LOGS_API),
            # Log messages to the console.
            logging.StreamHandler()
        ]
    )

# Get a logger instance for the application.
logger = logging.getLogger("clipforge")