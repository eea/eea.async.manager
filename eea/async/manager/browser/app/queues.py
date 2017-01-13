""" Async Browser Controllers
"""
import logging
from zc.twist import Failure
from zope.component import queryUtility, queryMultiAdapter
from plone.app.async.interfaces import IAsyncService
from Products.statusmessages.interfaces import IStatusMessage
from Products.Five.browser import BrowserView
from eea.async.manager.config import EEAMessageFactory as _
logger = logging.getLogger("eea.async.manager")

class Queue(BrowserView):
    """ Queue stats
    """
    def __init__(self, context, request):
        super(Queue, self).__init__(context, request)
        self._name = self.request.get('queue', '')
        self._queue = None
        self._dispatchers = None
        self._dead = None
        self._quotas = None
        # Jobs
        self._queued = None
        self._active = None
        self._failed = None
        self._finished = None

    @property
    def name(self):
        """ Queue name
        """
        return self._name

    @property
    def queue(self):
        """ zc.async queue
        """
        if self._queue is None:
            service = queryUtility(IAsyncService)
            if not service:
                return None
            self._queue = service.getQueues()[self.name]
        return self._queue

    @property
    def queued(self):
        """ Queued jobs
        """
        if self._queued is None:
            self.refresh()
        return self._queued

    @property
    def active(self):
        """ Active jobs
        """
        if self._active is None:
            self.refresh()
        return self._active

    @property
    def failed(self):
        """ Failed jobs
        """
        if self._failed is None:
            self.refresh()
        return self._failed

    @property
    def finished(self):
        """ Finished jobs
        """
        if self._finished is None:
            self.refresh()
        return self._finished

    @property
    def dispatchers(self):
        """ Get length of queue active dispatchers
        """
        if self._dispatchers is None:
            self.refresh()
        return self._dispatchers

    @property
    def dead(self):
        """ Get lenght of queue dead dispatchers
        """
        if self._dead is None:
            self.refresh()
        return self._dead

    @property
    def quotas(self):
        """ Get length of queue quotas
        """
        if self._quotas is None:
            self._quotas = len(self.queue.quotas)
        return self._quotas

    def refresh(self):
        """ Refresh jobs statistics
        """
        self._queue = None
        self._queued = self._active = self._failed = self._finished = 0
        self._dead = self._dispatchers = 0

        self._queued = len(self.queue)
        for dispatcher in self.queue.dispatchers.itervalues():
            if dispatcher.dead:
                self._dead += 1
            else:
                self._dispatchers += 1
            for agent in dispatcher.itervalues():
                self._active += len(agent)
                for job in agent.completed:
                    if isinstance(job.result, Failure):
                        self._failed += 1
                    else:
                        self._finished += 1

    def clear(self):
        """ Cleanup completed jobs
        """
        for dispatcher in self.queue.dispatchers.itervalues():
            for agent in dispatcher.itervalues():
                agent.completed.clear()

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        if 'queue' in kwargs:
            self._name = kwargs.get('queue', '')
            self.refresh()


class Queues(BrowserView):
    """ zc.async queues
    """
    def __init__(self, context, request):
        super(Queues, self).__init__(context, request)
        self._queues = None

    @property
    def queues(self):
        """ zc.async available queues
        """
        if self._queues is None:
            service = queryUtility(IAsyncService)
            if not service:
                return None
            self._queues = service.getQueues()
        return self._queues

    def queue(self, name=''):
        """ Refresh jobs statistics
        """
        queue = queryMultiAdapter((self.context, self.request),
                                  name='async-controlpanel-queue')
        queue(queue=name)
        return queue

    def redirect(self, msg='', msg_type='info', to=''):
        """ Set status message and redirect
        """
        if not to:
            to = self.context.absolute_url() + '/async-controlpanel-queues'
        if msg:
            IStatusMessage(self.request).add(msg, type=msg_type)
        self.request.response.redirect(to)

    def clear(self):
        """ Remove completed jobs including aborted ones
        """
        ids = self.request.get('ids', [])
        if not ids:
            return self.redirect(
                _(u"Please select at least one queue to cleanup"), 'error')

        for name in ids:
            self.queue(name).clear()

        return self.redirect(
            _(u"Successfully removed completed jobs from selected queues"))

    def __call__(self, **kwargs):
        if self.request.method.lower() == 'post':
            if self.request.get('form.button.Clear', None):
                return self.clear()
            return self.redirect(_(u"Invalid request"), 'error')
        return self.index()

