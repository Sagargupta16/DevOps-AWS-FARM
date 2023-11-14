import logging
import logging.config
import yaml

with open("config/logging.yml", "r") as f:
    logging.config.dictConfig(yaml.safe_load(f.read()))

logger = logging.getLogger(__name__)
logger.info("Logging configured")
