from .global_utils import LOG_DIR, LOGGING_CONFIG, CONFIG_FILE
from .misc_utils import load_yaml, make_dirs
import logging.config


def configure_logging():
    make_dirs(LOG_DIR)
    cfg= load_yaml(LOGGING_CONFIG)
    logging.config.dictConfig(cfg)

def load_config():
    return load_yaml(CONFIG_FILE)