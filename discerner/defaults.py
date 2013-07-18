"""
discerner.defaults
~~~~~~~~~~~~~~~~~~
"""
from logging import getLogger
from logging.config import dictConfig

analysis_interval = 14

log_config = {
    "version": 1,
    "formatters": {
        "simple": {
            "format": '%(asctime)s %(levelname)s - %(message)s',
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
}

# XXX Should be separated into its own configuration module!
logger = getLogger("root").root

dictConfig(log_config)
