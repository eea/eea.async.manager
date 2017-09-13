=================
EEA Async Manager
=================
.. image:: http://ci.eionet.europa.eu/job/eea/job/eea.async.manager/job/master/badge/icon
  :target: http://ci.eionet.europa.eu/job/eea/job/eea.async.manager/job/master/display/redirect

Manage plone.app.async (zc.async) queue via Plone > Site Setup


Contents
========

.. contents::


Main features
=============

* View and cleanup dead zc.async dispatchers
* View and cleanup completed jobs
* Browser jobs by status, dispatcher, quota

Install
=======

- Add eea.async.manager to your eggs section in your buildout and re-run buildout.
  You can download a sample buildout from
  https://github.com/eea/eea.async.manager/tree/master/buildouts/plone5
- Install *EEA Async Manager* within Site Setup > Add-ons


Getting started
===============

1. Go to *Plone > Site Setup > Async Queue Manager*


Dependencies
============

* plone.app.async


Source code
===========

- Latest source code (Plone 4/5 compatible):
  https://github.com/eea/eea.async.manager


Copyright and license
=====================
The Initial Owner of the Original Code is European Environment Agency (EEA).
All Rights Reserved.

The EEA Async Manager (the Original Code) is free software;
you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation;
either version 2 of the License, or (at your option) any later
version.

More details under docs/License.txt


Funding
=======

EEA_ - European Environment Agency (EU)

.. _EEA: http://www.eea.europa.eu/