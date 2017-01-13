""" Async Dispatchers
"""
import logging
from uuid import UUID
from zc.twist import Failure
from zope.component import queryUtility, queryMultiAdapter
from plone.app.async.interfaces import IAsyncService
from Products.statusmessages.interfaces import IStatusMessage
from Products.Five.browser import BrowserView
from eea.async.manager.config import EEAMessageFactory as _
logger = logging.getLogger("eea.async.manager")

class Dispatcher(BrowserView):
    """ zc.async queue dispatcher
    """
    def __init__(self, context, request):
        super(Dispatcher, self).__init__(context, request)
        self._qnane = self.request.get('queue', '')
        self._name = self.request.get('dispatcher', '')
        self._queue = None
        self._dispatcher = None
        self._agents = None
        # Jobs
        self._active = None
        self._failed = None
        self._finished = None

    @property
    def name(self):
        """ Queue name
        """
        return self._name

    @property
    def dead(self):
        """ Dispatcher is dead
        """
        return self.dispatcher.dead

    @property
    def queue(self):
        """ Get zc.async queue by name
        """
        if self._queue is None:
            service = queryUtility(IAsyncService)
            self._queue = service.getQueues()[self._qname]
        return self._queue

    @property
    def dispatcher(self):
        """ Get dispatcher in queue
        """
        if self._dispatcher is None:
            self._dispatcher = self.queue.dispatchers[self._name]
        return self._dispatcher

    @property
    def agents(self):
        """ Dispatcher agents len
        """
        if self._agents is None:
            self.refresh()
        return self._agents

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

    def refresh(self):
        """ Refresh jobs statistics
        """
        self._agents = 0
        self._active = self._failed = self._finished = 0
        for agent in self.dispatcher.itervalues():
            self._agents += 1
            self._active += len(agent)
            for job in agent.completed:
                if isinstance(job.result, Failure):
                    self._failed += 1
                else:
                    self._finished += 1

    def clear(self):
        """ Cleanup completed jobs
        """
        for agent in self.dispatcher.itervalues():
            agent.completed.clear()

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        if 'queue' in kwargs:
            self._qname = kwargs.get('queue')
        if 'name' in kwargs:
            self._name = kwargs.get('name')
            self.refresh()


class Dispatchers(BrowserView):
    """ zc.async queue dispatchers
    """
    def __init__(self, context, request):
        super(Dispatchers, self).__init__(context, request)
        self._name = self.request.get('queue', '')
        self._queue = None

    @property
    def name(self):
        """ Queue name
        """
        return self._name

    @property
    def queue(self):
        """ Get zc.async queue by name
        """
        if self._queue is None:
            service = queryUtility(IAsyncService)
            self._queue = service.getQueues()[self._name]
        return self._queue

    def dispatchers(self):
        """ Dispatchers
        """
        if self.queue is None:
            return

        for key, dispatcher in self.queue.dispatchers.iteritems():
            yield key, dispatcher

    def dispatcher(self, obj):
        """ Get dispatcher helper view
        """
        dispatcher = queryMultiAdapter((self.context, self.request),
                                  name='async-controlpanel-dispatcher')
        dispatcher._dispatcher = obj
        return dispatcher

    def delete(self):
        """ Remove dispatchers
        """
        ids = self.request.get('ids', [])
        if not ids:
            return self.redirect(
                _(u"Please select at least one dispatcher to delete"), 'error')

        for name in ids:
            uuid = UUID(name)
            da = self.queue.dispatchers[uuid]
            if da.activated:
                logger.warn("Can not remove active dispatcher %s", name)
                continue

            self.dispatcher(da).clear()
            # XXX Can't use unregister: TypeError: __init__() takes exactly 2...
            # self.queue.dispatchers.unregister(uuid)
            da = self.queue.dispatchers._data.pop(uuid)
            self.queue.dispatchers._len.change(-1)
            da.parent = da.name = None

        return self.redirect(
            _(u"Successfully removed selected dispatchers"))

    def redirect(self, msg='', msg_type='info', to=''):
        """ Set status message and redirect
        """
        if not to:
            to = self.context.absolute_url() + '/async-controlpanel-dispatchers'
        if msg:
            IStatusMessage(self.request).add(msg, type=msg_type)
        self.request.response.redirect(to)

    def __call__(self, **kwargs):
        if self.request.method.lower() == 'post':
            if self.request.get('form.button.Delete', None):
                return self.delete()
            elif self.request.get('form.button.Clear', None):
                return self.clear()
            return self.redirect(_(u"Invalid request"), 'error')
        return self.index()