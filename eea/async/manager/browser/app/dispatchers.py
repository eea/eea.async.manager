""" Async Dispatchers
"""
import logging
from uuid import UUID
from zc.twist import Failure
from zope.component import queryUtility
from plone.app.async.interfaces import IAsyncService
from Products.statusmessages.interfaces import IStatusMessage
from Products.Five.browser import BrowserView
from eea.async.manager.config import EEAMessageFactory as _
from eea.async.manager.interfaces import IDispatcherInfo
logger = logging.getLogger("eea.async.manager")


class Dispatcher(object):
    """ zc.async queue dispatcher
    """
    def __init__(self, context):
        self.context = context

        self._agents = None
        # Jobs
        self._active = None
        self._failed = None
        self._finished = None

    @property
    def dead(self):
        """ Dispatcher is dead
        """
        return self.context.dead

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
        for agent in self.context.itervalues():
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
        for agent in self.context.itervalues():
            agent.completed.clear()


class Dispatchers(BrowserView):
    """ zc.async queue dispatchers
    """
    def __init__(self, context, request):
        super(Dispatchers, self).__init__(context, request)
        self._qname = self.request.get('queue', '')
        self._queue = None

    @property
    def qname(self):
        """ Queue name
        """
        return self._qname

    @property
    def queue(self):
        """ Get zc.async queue by name
        """
        if self._queue is None:
            service = queryUtility(IAsyncService)
            self._queue = service.getQueues()[self.qname]
        return self._queue

    def dispatchers(self):
        """ Dispatchers
        """
        if self.queue is None:
            return

        for key, dispatcher in self.queue.dispatchers.iteritems():
            yield key, dispatcher

    def dispatcher_info(self, dispatcher):
        """ Get dispatcher helper view
        """
        return IDispatcherInfo(dispatcher)

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

            self.dispatcher_info(da).clear()
            # XXX Can't use unregister method due to zc.async bug #1
            # See https://github.com/zopefoundation/zc.async/issues/1

            # self.queue.dispatchers.unregister(uuid)
            #
            da = self.queue.dispatchers._data.pop(uuid)
            self.queue.dispatchers._len.change(-1)
            da.parent = da.name = None
            #
            # End of custom un-register

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
