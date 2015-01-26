"""
Summarizer dispatcher.
"""
import config
import logging, logging.config, yaml
logging.config.dictConfig(yaml.load(config.LOGGING))
logger = logging.getLogger(__name__)

import time
from twitter import queue


def dispatch():
    "Summarizing new statuses."
    while True:
        queue.enqueue()
        logger.debug('Sleeping')
        time.sleep(queue.FREQUENCY)
