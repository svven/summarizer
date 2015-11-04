"""
Summarizer Twitter queue.
"""
import logging
logger = logging.getLogger(__name__)

from . import config, db, r

from job import StatusJob
from database.twitter.models import User, State, Status

import time, datetime
from rq import Connection, Queue

QUEUE = config.SUMMARIZER_QUEUE
LIMIT = 300 # statuses
FREQUENCY = 1 # 1 sec
RESULT_TTL = 1 * 60 # 1 min
TIMEOUT = 5 * 60 # 5 min


def process(status_id):
    "Process specified status."
    logger.debug("Start process")
    session = db.session()
    failed = False # yet
    status = session.query(Status).filter_by(status_id=status_id).one()
    try:
        job = StatusJob(status)
        job.do(session)
        failed = job.failed # may be True
        logger.info("Proced %s: %s",
            unicode(status).encode('utf8'), job.result)
        return job.result
    except Exception, e:
        session.rollback()
        failed = True # obviously
        logger.error("Failed %s: %s", 
            unicode(status).encode('utf8'), repr(e))
        raise
    finally:
        try:
            status = session.merge(status) # no need
            status.state = failed and State.FAIL or State.DONE
            session.commit()
        except:
            session.rollback()
        session.close()
        logger.debug("End process")

def enqueue(statuses=[]):
    "Enqueue statuses to process."
    now = datetime.datetime.utcnow()
    logger.debug("Start enqueue")
    session = db.session()
    try:
        if not statuses:
            statuses = session.query(Status).\
                filter(Status.state == State.NONE).\
                order_by(Status.created_at.desc()).limit(LIMIT)
        else:
            statuses = [session.merge(s) for s in statuses]
        with Connection(r):
            q = Queue(QUEUE)
            for status in statuses:
                status_id = status.status_id
                description = unicode(status).encode('utf8')
                job = q.enqueue_call(func=process, args=(status_id,), 
                    description=description, result_ttl=RESULT_TTL, timeout=TIMEOUT) # job_id=unicode(status_id), result_ttl=0
                status.state = State.BUSY
                logger.debug('Queued: %s', description)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
        logger.debug("End enqueue")
