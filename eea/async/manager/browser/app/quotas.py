""" Async Quotas
"""
import logging
from zope.component import queryUtility
from plone.app.async.interfaces import IAsyncService
from Products.Five.browser import BrowserView
from eea.async.manager.interfaces import IQuotaInfo
logger = logging.getLogger("eea.async.manager")

class Quota(object):
    """ Quota Info
    """
    def __init__(self, context):
        self.context = context
        self._queued = None

    @property
    def queued(self):
        """ Queued jobs in quota
        """
        if self._queued is None:
            self._queued = len(self.context)
        return self._queued


class Quotas(BrowserView):
    """ zc.async queue quotas
    """
    def __init__(self, context, request):
        super(Quotas, self).__init__(context, request)
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

    def quotas(self):
        """ Quotas
        """
        if self.queue is None:
            return

        for key, quota in self.queue.quotas.iteritems():
            yield key, quota

    def quota_info(self, quota):
        """ Get Quoata info
        """
        return IQuotaInfo(quota)
