"""
Summarizer Twitter queue.
"""
from . import config, db, r
from job import StatusJob

from database.twitter.models import User, State, Status

import time, datetime
from rq import Connection, Queue

QUEUE = config.SUMMARIZER_QUEUE
LIMIT = 300 # statuses
FREQUENCY = 1 * 60 # 1 min


def process(status_id):
    "Process specified status."
    session = db.Session()
    try:
        status = session.query(Status).filter_by(status_id=status_id).one()
        job = StatusJob(status)
        job.do(session)
        status = session.merge(status) # no need
        status.state = job.failed and State.FAIL or State.DONE
        session.commit()
        return job.result
    except:
        session.rollback()
        raise
    finally:
        session.close()

def enqueue(statuses=[]):
    "Enqueue statuses to process."
    now = datetime.datetime.utcnow()
    session = db.Session()
    try:
    	if not statuses:
        	statuses = session.query(Status).\
	            filter(Status.link_id == None, Status.state == State.NONE).\
	            order_by(Status.created_at).limit(LIMIT)
        else:
        	statuses = [session.merge(s) for s in statuses]
        with Connection(r):
            q = Queue(QUEUE)
            for status in statuses:
                status_id = status.status_id
                job = q.enqueue_call(func=process, args=(status_id,), 
                    description=status) # job_id=unicode(status_id), result_ttl=0
                status.state = State.BUSY
                session.commit()
                print '%s Queued: %s' % (time.strftime('%X'), status)
    except:
        session.rollback()
        raise
    finally:
        session.close()
