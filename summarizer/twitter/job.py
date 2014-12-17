"""
Summarizer Twitter job.
"""
from . import config, db, summary

from summary import Summary

from database.db import IntegrityError
from database.twitter.models import User, Status
from database.news.models import Link, Reader, Source, Mark

import datetime

NEW_LINK, EXISTING_LINK, BAD_LINK, SKIPPED_LINK = (
    'new', 'existing', 'bad', 'skipped') #, 'restricted'


class StatusJob(object):
    "Summarizer job for a Twitter status."

    def __init__(self, status):
        "Initialize the status model."
        assert status and status.url, \
            'Bad or missing StatusJob arg.'

        self.status = status

        self.failed = False # yet
        self.started_at = None
        self.ended_at = None

        self.link = None # return
        self.result = None

    def update_status(self, session):
        "Update status link at the end."
        status = session.merge(self.status) # just in case
        if self.link:
            status.link_id = self.link.id

    # def create_mark(self, session):
    #     "Create mark for reader and link."
    #     mark = None
    #     # moment = munixtime(self.status.created_at)
    #     mark = Mark(link_id=self.link.id) #, moment=moment, source=Source.TWITTER
    #     session.add(mark)
    #     reader = session.query(Reader).filter_by(twitter_user_id=self.status.user_id).first()
    #     if not reader:
    #         reader = Reader(twitter_user_id=self.status.user_id)
    #         session.add(reader)
    #     reader.marks.append(mark)
    #     return mark

    def load_link(self, session, url):
        "Load link from URL."
        link = result = None
        status = session.query(Status).\
            filter(Status.url == url, Status.link_id != None).first()
        if status: # 
            link = session.query(Link).get(status.link_id)
        else:
            link = session.query(Link).filter_by(url=url).first()
        if link: # existing link
            result = EXISTING_LINK
            return link, result

        def check_url(url):
            pass

        summary = Summary(url)
        summary.extract(check_url=check_url)
        link = Link(summary)
        session.add(link)
        result = NEW_LINK
        return link, result


    def do(self, session):
        """
        Create the news link based on status URL.
        """
        assert self.status.url, 'URL missing, can\'t do the job.'
        self.started_at = datetime.datetime.utcnow()
        link = result = None
        try:
            url = self.status.url
            link, result = self.load_link(session, url)
            if session.new: # new
                session.commit() # atomic
        except IntegrityError: # existing
            session.rollback()
            result = SKIPPED_LINK
        # except Exception, e:
        #     session.rollback()
        #     result = BAD_LINK
        #     self.failed = True
        #     print e # warning
        if link: # new or existing
            self.link = link
        self.result = result
        print "%s: %s" % (result.capitalize(), 
            unicode(link or self.status).encode('utf8'))
        # TODO: self.load_mark(session)
        self.update_status(session)
        # session.commit() # outside
        self.ended_at = datetime.datetime.utcnow()

