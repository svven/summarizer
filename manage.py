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
def enqueue(loop=False):
    "Enqueue new statuses to be processed."
    from summarizer.twitter import queue
    while True:
        queue.enqueue()
        if not loop:
            break
        time.sleep(queue.FREQUENCY)

@manager.command
def work():
    "Custom rqworker processing the queue."
    from summarizer import r, summary
    rules = summary.filters.AdblockURLFilter.rules # force
    with Connection(r):
        worker = Worker([Queue(config.SUMMARIZER_QUEUE)])
        if config.SENTRY_DSN:
            from raven import Client
            from rq.contrib.sentry import register_sentry
            client = Client(config.SENTRY_DSN)
            register_sentry(client, worker)
        worker.work()

@manager.command
def process(status_id):
    "Process specified status right now."
    from summarizer.twitter import queue
    queue.process(status_id)


if __name__ == '__main__':
    manager.main()