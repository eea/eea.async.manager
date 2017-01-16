# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IEEAAsyncManagerLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IQueueInfo(Interface):
    """ Async Queue info
    """


class IDispatcherInfo(Interface):
    """ Async Dispatcher info
    """


class IQuotaInfo(Interface):
    """ Async Quota info
    """


class IJobInfo(Interface):
    """ Async Job info
    """
