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
def enqueue(burst=False):
    "Enqueue new statuses to be processed."
    from summarizer.twitter import queue
    while True:
        queue.enqueue()
        if burst:
            break
        time.sleep(queue.FREQUENCY)

@manager.command
def work(burst=False):
    "Queue worker processing statuses."
    from summarizer import r, summary
    rules = summary.filters.AdblockURLFilter.rules # force
    with Connection(r):
        worker = Worker([Queue(config.SUMMARIZER_QUEUE)])
        worker.work(burst)

@manager.command
def process(status_ids):
    "Process comma separated status ids."
    from summarizer.twitter import queue
    for status_id in str(status_ids).split(','):
        queue.process(status_id.strip())


if __name__ == '__main__':
    manager.main()