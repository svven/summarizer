"""
Summarizer Twitter job.
"""
from . import config, db, summary

from summary import Summary, HTMLParseError
from requests.exceptions import HTTPError, Timeout

from database.db import IntegrityError
from database.twitter.models import User, Status
from database.news.models import Link, Reader, Source, Mark

import datetime

NEW_LINK, EXISTING_LINK, BAD_LINK = (
    'new', 'existing', 'bad') #, 'restricted'


class ExistingLinkException(Exception):
    pass
class RestrictedLinkException(Exception):
    pass

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
        status.link_id = self.link.id

    def load_mark(self, session):
        "Load mark for reader and link."
        mark = None
        twitter_user_id = self.status.user_id
        reader = session.query(Reader).filter_by(twitter_user_id=twitter_user_id).first()
        if not reader:
            reader = Reader(twitter_user_id=twitter_user_id)
            session.add(reader)
            session.commit() # atomic
        mark = Mark(self.status, reader.id)
        session.add(mark)
        # reader.marks.append(mark)
        return mark

    def get_link(self, session, url):
        "Get link from database by URL."
        link = None
        status = session.query(Status).\
            filter(Status.url == url, Status.link_id != None).first()
        if status: # 
            link = session.query(Link).get(status.link_id)
        else:
            link = session.query(Link).filter_by(url=url).first()
        return link

    def load_link(self, session, url):
        """
        Load link from URL.
        Get it from database, or use `summary` to create it. The returned
        `link.url` is most probably different from the `url` input param.
        """
        def check_url(url,
            get_link=lambda u: self.get_link(session, u)):
            """
            Raise for existing or restricted URLs.
            Param `url` is actually `summary.url` while extracting.
            """
            print "Checking"
            link = get_link(url) # self.get_link(session, url)
            if link: # existing
                raise ExistingLinkException()

        link = self.get_link(session, url)
        if link: # existing
            result = EXISTING_LINK
        else: # summarize
            summary = Summary(url)
            try:
                print "Summarizing"
                summary.extract(check_url=check_url)
                print "Summarized"
                link = Link(summary) # new
                session.add(link)
                result = NEW_LINK
            except ExistingLinkException: # existing
                link = self.get_link(session, summary.url)
                result = EXISTING_LINK
            # except RestrictedLinkException:
            #     result = RESTRICTED_LINK
        return link, result

    def do(self, session):
        """
        Create the news link based on status URL.
        """
        print "Start job"
        assert self.status.url, 'URL missing, can\'t do the job.'
        self.started_at = datetime.datetime.utcnow()
        link = result = None
        url = self.status.url
        try:
            link, result = self.load_link(session, url)
            if session.new: # new
                session.commit() # atomic
        except IntegrityError, e: # existing
            if link:
                url = link.url # after redirects
            session.rollback()
            link = self.get_link(session, url)
            if link: # existing
                result = EXISTING_LINK
                print repr(e), self.status.id # warning
            else: # existing but not found, fail
                self.failed = True # redundant
                raise e
        except (HTTPError, HTMLParseError), e:
            session.rollback()
            result = BAD_LINK
            self.failed = True
            print repr(e), self.status.id # warning
        # except Timeout, e:
        #     raise e
        self.result = result
        print "%s: %s" % (result.capitalize(), 
            unicode(link or self.status).encode('utf8'))
        if link and link.id: # new or existing
            self.link = link
            self.update_status(session) # sets self.status.link_id
            self.load_mark(session) # needs self.status.link_id set
        session.commit() # outside
        self.ended_at = datetime.datetime.utcnow()
        print "End job"

