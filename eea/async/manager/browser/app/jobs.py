""" Async Quotas
"""
import logging
import operator
from urllib import urlencode
from uuid import UUID
from zc.twist import Failure
from zc.async.interfaces import COMPLETED
from zope.component import queryUtility
from plone.app.async.interfaces import IAsyncService
from plone.batching import Batch
from ZODB.utils import u64
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from eea.async.manager.interfaces import IJobInfo
from eea.async.manager.config import EEAMessageFactory as _
logger = logging.getLogger("eea.async.manager")


class Job(object):
    """ zc.async job info
    """
    def __init__(self, context):
        self.context = context
        self._status = None
        self._result = None
        self._start = None
        self._end = None

    @property
    def oid(self):
        """ Job id
        """
        return u64(self.context._p_oid)

    @property
    def status(self):
        """ Job status
        """
        if self._status is None:
            if self.context.status == COMPLETED:
                if isinstance(self.context.result, Failure):
                    self._status = 'failed'
                    return self._status
            self._status = self.context.status.replace('-status', '')
        return self._status

    @property
    def progress(self):
        """ Job Progress
        """
        if self.status == 'running':
            return ''

        progress = self.context.annotations.get('progress', 0.0) * 100
        if not progress:
            return ''

        return progress

    @property
    def callable(self):
        """ Job callable
        """
        return self.context.callable.__name__

    @property
    def args(self):
        """ Job args
        """
        index = 0
        if self.callable == '_executeAsUser':
            context_path = self.context.args[0]
            yield True, u"/".join(context_path)

            portal_path = self.context.args[1]
            yield False, u"/".join(portal_path)

            uf_path = self.context.args[2]
            yield False, u"/".join(uf_path)

            user_id = self.context.args[3]
            yield False, user_id

            func_name = self.context.args[4]
            yield True, func_name.__name__

            index = 5

        for arg in self.context.args[index:]:
            yield False, arg

    @property
    def details(self):
        """ Detailed results
        """
        if isinstance(self.context.result, Failure):
            return self.context.result.getTraceback()
        return self.context.result

    @property
    def result(self):
        """ Job args
        """
        if isinstance(self.context.result, Failure):
            return self.context.result.getErrorMessage()
        return self.context.result

    @property
    def start(self):
        """ Job start
        """
        if self._start is None:
            self._start = getattr(self.context, 'active_start', None)
            if not self._start:
                self._start = getattr(self.context, 'begin_after', None)
        return self._start

    @property
    def end(self):
        """ Job end
        """
        if self._end is None:
            self._end = self.context.active_end
        return self._end

    def strftime(self, date, fmt='%Y-%m-%d %H:%M:%S'):
        """ Date to strftime
        """
        if hasattr(date, 'strftime'):
            return date.strftime(fmt)
        return ''



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

    @property
    def url(self):
        """ View URL
        """
        url = self.context.absolute_url() + "/async-controlpanel-jobs?"
        url += urlencode(dict(
            queue=self.qname,
            dispatcher=self.dname,
            quota=self.qtname,
            status=self.status
        ))
        return url


    def quota_jobs(self, quota=None):
        """ Quota jobs
        """
        if quota is None:
            quota = self.quota

        for job in quota:
            yield IJobInfo(job)

    def dispatcher_jobs(self, dispatcher=None, status=None):
        """ Dispatcher jobs
        """
        if dispatcher is None:
            dispatcher = self.dispatcher

        if status is None:
            status = self.status

        for agent in dispatcher.itervalues():
            if not status:
                for job in agent:
                    yield IJobInfo(job)
                return

            for job in agent.completed:
                if status == 'failed':
                    if isinstance(job.result, Failure):
                        yield IJobInfo(job)
                else:
                    if not isinstance(job.result, Failure):
                        yield IJobInfo(job)

    def queue_jobs(self, queue=None):
        """ Queue jobs
        """
        if queue is None:
            queue = self.queue

        status = self.status
        if not status:
            for job in queue:
                yield IJobInfo(job)
            return

        if status == 'active':
            status = ''

        for dispatcher in queue.dispatchers.itervalues():
            for info in self.dispatcher_jobs(dispatcher, status=status):
                yield info

    def jobs(self):
        """ Jobs
        """
        if self.quota is not None:
            results = self.quota_jobs()
        elif self.dispatcher is not None:
            results = self.dispatcher_jobs()
        else:
            results = self.queue_jobs()

        b_start = self.request.get('b_start', 0)
        b_size = self.request.get('b_size', 20)
        results = sorted(
            results, key=operator.attrgetter('start'), reverse=True)
        return Batch(results, b_size, start=b_start)

    def delete(self):
        """ Remove Jobs
        """
        ids = self.request.get("ids", [])
        if not ids:
            return self.redirect(
                _(u"Please select at least one job to delete"), "error")

        delete = set()
        for job in self.queue:
            if str(IJobInfo(job).oid) in ids:
                delete.add(job)

        for job in delete:
            self.queue.remove(job)

        return self.redirect(
                _(u"Successfully removed selected jobs"))

    def redirect(self, msg='', msg_type='info', to=''):
        """ Set status message and redirect
        """
        if not to:
            to = self.url
        if msg:
            IStatusMessage(self.request).add(msg, type=msg_type)
        self.request.response.redirect(to)

    def __call__(self, **kwargs):
        if self.request.method.lower() == 'post':
            if self.request.get('form.button.Delete', None):
                return self.delete()
            return self.redirect(_(u"Invalid request"), 'error')
        return self.index()
