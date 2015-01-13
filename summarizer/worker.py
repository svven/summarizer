"""
Summarizer worker.
"""
import sys
from rq import Queue, Connection, Worker

# import requests
# # https://urllib3.readthedocs.org/en/latest/security.html
# requests.packages.urllib3.disable_warnings()

import logging
# logging.getLogger("requests").setLevel(logging.DEBUG)
# import httplib
# httplib.HTTPConnection.debuglevel = 1

# logging.basicConfig() # you need to initialize logging, otherwise you will not see anything from requests
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

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