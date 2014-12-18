"""
Summarizer worker.
"""
import sys
from rq import Queue, Connection, Worker

# Preload libraries
from . import config, r, summary
rules = summary.filters.AdblockURLFilter.rules # force

QUEUE = config.SUMMARIZER_QUEUE


# Provide queue names to listen to as arguments to this script,
# similar to rqworker
with Connection(r):
    qs = map(Queue, sys.argv[1:]) or [Queue(QUEUE)]
    w = Worker(qs)
    w.work()