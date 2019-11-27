""" Recover Async
"""
from zope.component import queryUtility
from plone.app.async.interfaces import IAsyncService
from Products.Five.browser import BrowserView
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from eea.async.manager.interfaces import IDispatcherInfo
from eea.async.manager.config import EEAMessageFactory as _


class Recover(BrowserView):
    """ Recover zc.async queue
    """
    template = ViewPageTemplateFile('../zpt/recover.pt')

    def __init__(self, context, request):
        super(Recover, self).__init__(context, request)
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

    def jobs(self):
        """ Next jobs in queue
        """
        for job in self.queue:
            yield job

    def dispatchers(self):
        """ Dispatchers
        """
        if self.queue is None:
            return

        for key, dispatcher in self.queue.dispatchers.iteritems():
            yield key, dispatcher
    #
    # Actions
    #
    def delete_next_job(self):
        """ Return next jobs in queue
        """
        for job in self.jobs():
            self.queue.remove(job)
            return self.redirect("Successfully removed job: %s" % job)
        return self.redirect(_("There is no job in queue to be deleted."))

    def delete_dead_dispatchers(self):
        """ Remove dead dispatchers
        """
        for uuid, da in self.dispatchers():
            if da.activated:
                continue

            IDispatcherInfo(da).clear()
            # XXX Can't use unregister method due to zc.async bug #1
            # See https://github.com/zopefoundation/zc.async/issues/1

            # self.queue.dispatchers.unregister(uuid)
            #
            da = self.queue.dispatchers._data.pop(uuid)
            self.queue.dispatchers._len.change(-1)
            da.parent = da.name = None
            #
            # End of custom un-register

        return self.redirect(_(u"Successfully removed dead dispatchers"))
    #
    # Return
    #
    def redirect(self, msg='', msg_type='info', to=''):
        """ Set status message and redirect
        """
        if not to:
            to = self.context.absolute_url() + '/async-controlpanel-recover'
        if msg:
            IStatusMessage(self.request).add(msg, type=msg_type)
        self.request.response.redirect(to)

    def __call__(self, **kwargs):
        if self.request.method.lower() == 'post':
            if self.request.get('form.button.delete.job', None):
                return self.delete()
            elif self.request.get('form.button.delete.dispachers', None):
                return self.clear()
            return self.redirect(_(u"Invalid request"), 'error')
        return self.index()
