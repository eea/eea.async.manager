""" Async Quotas
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

class Quotas(BrowserView):
    """ zc.async queue quotas
    """
    def __init__(self, context, request):
        super(Quotas, self).__init__(context, request)
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

    def quotas(self):
        """ Quotas
        """
        if self.queue is None:
            return

        for key, quota in self.queue.quotas.iteritems():
            yield key, quota
