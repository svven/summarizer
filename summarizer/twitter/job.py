"""
Summarizer Twitter job.
"""
import logging
logger = logging.getLogger(__name__)

from . import config, db, summary, aggregator

from summary import Summary, HTMLParseError
from requests.exceptions import HTTPError, Timeout

from database.db import IntegrityError
from database.models import *

from aggregator.models import Reader as AggregatorReader

import datetime

NEW_LINK, EXISTING_LINK, UPDATED_LINK, BAD_LINK = (
    'new', 'existing', 'updated', 'bad') #, 'restricted'


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
        self.redo = False # yet

        self.failed = False # yet
        self.started_at = None
        self.ended_at = None

        self.link = None # return
        self.result = None

    def update_status(self, session):
        "Update status link at the end."
        status = session.merge(self.status) # just in case
        status.link_id = self.link.id

    def load_pick(self, session):
        "Load pick for reader and link."
        pick = None
        status = self.status
        unpick = status.pick # current
        if unpick: # redo
            logger.debug("Delete old pick")
            session.delete(unpick)
            session.commit()
        twitter_user_id = status.user_id
        reader = session.query(Reader).\
            filter_by(twitter_user_id=twitter_user_id).first()
        if not reader:
            reader = Reader(twitter_user_id=twitter_user_id)
            session.add(reader)
            session.commit() # atomic
        elif reader.ignored:
            logger.warning("Ignored: %s", unicode(reader).encode('utf8'))
        elif status.link.ignored:
            logger.warning("Ignored: %s", unicode(status.link).encode('utf8'),
                extra={'data': {'id': status.status_id, 'url': status.url}})
        else:
            pick = Pick(status, reader.id)
            session.add(pick)
            # reader.picks.append(pick)
        return pick

    def get_link(self, session, url):
        "Get existing link from database by URL."
        link = None
        status = session.query(Status).\
            filter(Status.url == url, Status.link_id != None, 
                Status.link_id != self.status.link_id).first()
        if status:
            link = session.query(Link).get(status.link_id)
        else:
            link = session.query(Link).filter_by(url=url).first()
        return link

    def load_link(self, session, url):
        """
        Load link from URL.
        Get it from database, or use `summary` to create it. The returned
        `link.url` is most probably different from the `url` input param.
        When `redo` mode perform resummarization and update current link.
        """
        def check_url(url):
            """
            Raise for existing or restricted URLs.
            Param `url` is actually `summary.url` while extracting.
            """
            logger.debug("Checking")
            link = self.get_link(session, url)
            if link: # existing
                raise ExistingLinkException()

        if self.redo: # redo
            s = Summary(url)
            logger.debug("Resummarizing")
            s.extract()
            logger.debug("Resummarized")
            link = self.status.link # current
            if link and \
                link.url == s.url: # same url
                link.load(s)
                # link.updated = True
                result = UPDATED_LINK
            else: # new url
                link = Link(s)
                result = NEW_LINK
            session.add(link)
        else: # just do
            link = self.get_link(session, url)
            if link: # existing
                result = EXISTING_LINK
            else: # summarize
                s = Summary(url)
                try:
                    logger.debug("Summarizing")
                    s.extract(check_url=check_url)
                    logger.debug("Summarized")
                except ExistingLinkException: # existing
                    link = self.get_link(session, s.url)
                    result = EXISTING_LINK
                # except RestrictedLinkException:
                #     result = RESTRICTED_LINK
                else: # new
                    link = Link(s)
                    session.add(link)
                    result = NEW_LINK
        return link, result

    def do(self, session):
        """
        Create the news link based on status URL.
        """
        logger.debug("Start job")
        assert self.status.url, 'URL missing, can\'t do the job.'
        self.started_at = datetime.datetime.utcnow()
        self.redo = self.status.link_id is not None # redo
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
            else: # existing but not found, fail
                self.failed = True # redundant
                logger.error("Existing link not found", 
                    exc_info=True, extra={'data': {'id': self.status.id, 'url': url}})
                raise e
        except (HTTPError, HTMLParseError), e: # , Timeout
            session.rollback()
            result = BAD_LINK
            self.failed = True
            logger.warning("Bad: %s", 
                unicode(link or self.status).encode('utf8'),
                exc_info=True, extra={'data': {'id': self.status.id, 'url': url}})
        else:
            logger.debug(result.capitalize() + ": %s", 
                unicode(link or self.status).encode('utf8'),
                extra={'data': {'id': self.status.id, 'url': url}})
        self.result = result
        if link and link.id: # new or existing
            self.link = link
            self.update_status(session) # sets self.status.link_id
            self.load_pick(session) # needs self.status.link_id set
        session.commit() # outside
        self.ended_at = datetime.datetime.utcnow()
        logger.debug("End job")


@db.event.listens_for(Pick, "after_insert")
def after_insert_pick(mapper, connection, pick):
    logger.debug("Picking")
    try:
        reader = AggregatorReader(pick.reader_id)
        reader.pick(pick.link_id, pick.moment)
        reader.rem_picks() # real time clean up
    except Exception, e:
        logger.error("Aggregator pick failed", exc_info=True)

@db.event.listens_for(Pick, "after_delete")
def after_delete_pick(mapper, connection, pick):
    logger.debug("Unpicking")
    try:
        reader = AggregatorReader(pick.reader_id)
        reader.unpick(pick.link_id)
    except Exception, e:
        logger.error("Aggregator unpick failed", exc_info=True)
