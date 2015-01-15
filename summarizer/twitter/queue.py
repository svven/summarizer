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
RESULT_TTL = 1 * 60 # 1 min


def process(status_id):
    "Process specified status."
    print "Start process"
    session = db.Session()
    failed = False # yet
    status = session.query(Status).filter_by(status_id=status_id).one()
    try:
        job = StatusJob(status)
        job.do(session)
        failed = job.failed # may be True
        return job.result
    except:
        session.rollback()
        failed = True # obviously
        raise
    finally:
        status = session.merge(status) # no need
        status.state = failed and State.FAIL or State.DONE
        session.commit()
        session.close()
        print "End process"

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
                description = unicode(status).encode('utf8')
                job = q.enqueue_call(func=process, args=(status_id,), 
                    description=description, result_ttl=RESULT_TTL) # job_id=unicode(status_id), result_ttl=0
                status.state = State.BUSY
                session.commit()
                print '%s Queued: %s' % (time.strftime('%X'), description)
    except:
        session.rollback()
        raise
    finally:
        session.close()
