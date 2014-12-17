"""
Summarizer dispatcher.
"""
import time
from twitter import queue


def dispatch():
    "Summarizing new statuses."
    while True:
        queue.enqueue()
        print '%s Sleeping' % time.strftime('%X')
        time.sleep(queue.FREQUENCY)
