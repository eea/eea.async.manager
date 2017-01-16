""" Async Quotas
"""
import logging
from uuid import UUID
from zc.twist import Failure
from zope.component import queryUtility
from plone.app.async.interfaces import IAsyncService
from Products.Five.browser import BrowserView
logger = logging.getLogger("eea.async.manager")


class Jobs(BrowserView):
    """ zc.async queue quotas
    """
    def __init__(self, context, request):
        super(Jobs, self).__init__(context, request)
        self._qname = self.request.get('queue', '')
        self._dname = self.request.get('dispatcher', '')
        self._qtname = self.request.get('quota', '')
        self._status = self.request.get('status', '')
        self._queue = None
        self._dispatcher = None
        self._quota = None

    @property
    def qname(self):
        """ Dispatcher name
        """
        return self._qname

    @property
    def dname(self):
        """ Dispatcher name
        """
        return self._dname

    @property
    def qtname(self):
        """ Quota name
        """
        return self._qtname

    @property
    def status(self):
        """ Filter jobs by status
        """
        return self._status

    @property
    def queue(self):
        """ Get zc.async queue by name
        """
        if self._queue is None:
            service = queryUtility(IAsyncService)
            self._queue = service.getQueues()[self.qname]
        return self._queue

    @property
    def dispatcher(self):
        """ Dispatcher
        """
        if self._dispatcher is None:
            if not self.dname:
                return

            if self.queue is None:
                return self._quota

            uuid = UUID(self.dname)
            self._dispatcher = self.queue.dispatchers[uuid]
        return self._dispatcher

    @property
    def quota(self):
        """ Quota
        """
        if self._quota is None:
            if not self.qtname:
                return self._quota

            if self.queue is None:
                return self._quota

            self._quota = self.queue.quotas[self.qtname]
        return self._quota

    def quota_jobs(self, quota=None):
        """ Quota jobs
        """
        if quota is None:
            quota = self.quota

        for job in quota:
            yield job.key, job

    def dispatcher_jobs(self, dispatcher=None):
        """ Dispatcher jobs
        """
        if dispatcher is None:
            dispatcher = self.dispatcher

        for agent in dispatcher.itervalues():
            if not self.status:
                for job in agent:
                    yield job.key, job
                return

            for job in agent.completed:
                if self.status == 'failed':
                    if isinstance(job.result, Failure):
                        yield job.key, job
                else:
                    if not isinstance(job.result, Failure):
                        yield job.key, job

    def queue_jobs(self, queue=None):
        """ Queue jobs
        """
        if queue is None:
            queue = self.queue

        if not self.status:
            for job in queue:
                yield job.key, job
            return

        for dispatcher in queue.dispatchers.itervalues():
            for key, job in self.dispatcher_jobs(dispatcher):
                yield key, job

    def jobs(self):
        """ Jobs
        """
        if self.quota is not None:
            return self.quota_jobs()

        if self.dispatcher is not None:
            return self.dispatcher_jobs()

        return self.queue_jobs()
