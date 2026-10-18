import logging
import logging.config
import os
import yaml

with open("config/logging.yml", "r") as f:
    log_config = yaml.safe_load(f.read())

# LOG_FORMAT=json (set in the Docker image) swaps the text formatter for one JSON object per line
if os.getenv("LOG_FORMAT", "text").lower() == "json":
    log_config["formatters"]["defaultFormatter"] = {
        "()": "config.json_formatter.JsonFormatter"
    }

logging.config.dictConfig(log_config)

logger = logging.getLogger(__name__)
logger.info("Logging configured")
