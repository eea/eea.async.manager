""" Recover Async
"""
from Products.Five.browser import BrowserView
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile


class Recover(BrowserView):
    """ Recover zc.async queue
    """
    template = ViewPageTemplateFile('../zpt/recover.pt')

    def __call__(self, **kwargs):
        return self.index()
