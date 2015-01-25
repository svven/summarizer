"""
Summarizer dispatcher.
"""
from . import logging
logger = logging.getLogger(__name__)

import time
from twitter import queue


def dispatch():
    "Summarizing new statuses."
    while True:
        queue.enqueue()
        logger.debug('Sleeping for %s seconds.', queue.FREQUENCY)
        time.sleep(queue.FREQUENCY)
