"""
Summarizer manager.
"""
from summarizer import config
import logging, logging.config, yaml
logging.config.dictConfig(yaml.load(config.LOGGING))

from manager import Manager
manager = Manager()

import sys, time
from rq import Queue, Connection, Worker


@manager.command
def process(status_id):
    "Process specified twitter status by id."
    from summarizer.twitter import queue
    queue.process(status_id)

@manager.command
def enqueue(loop=False):
    "Enqueue new statuses to be processed."
    from summarizer.twitter import queue
    logger = logging.getLogger('summarizer')
    while True:
        queue.enqueue()
        if not loop:
            break
        logger.info('Sleeping')
        time.sleep(queue.FREQUENCY)


if __name__ == '__main__':
    manager.main()