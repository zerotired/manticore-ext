:date: 2011-03-23

.. _manticore-ext-changes:

============================
Manticore extensions CHANGES
============================

.. include:: manticore-links.rst

2013-08-25 0.1.1
================
- let aggregated changes .rst include the global/manticore-links.rst

2013-08-25 0.1.0
================
- refactored to ``zt.manticore.ext`` namespace
- various cleanups and enhancements

2011-11-22 0.0.5
================
- introduced "laig - lightweight artifact interconnection grapher" based on Graphviz_

2011-11-15 0.0.4
================
- deactivated video- and statistics-processing on ``*-develop`` branches
- introduced Sphinx_ extension sphinxcontrib-feed_ to render a list of recent changes

2011-11-06 0.0.3
================
- expand symbols like ``:bug:`XXXX``` to interlink with trac_ instance
- additionally run gitstats_ across **all** git projects

2011-10-21 0.0.2
================
- ``zt.manticore.ext.gource``: source code repository visualization using Gource_
- ``zt.manticore.ext.changes``: visualize all changes using the fine `SIMILE Timeline Widget`_
- ``zt.manticore.ext.statistics``: generate repository statistics using GitStats_ and StatSVN_

2011-03-23 0.0.1
================
- ``zt.manticore.ext.changes``: automatic reStructuredText_ generation of aggregated, chronological changes across all projects
- ``zt.manticore.ext.bugseverywhere``: automatic html generation of BugsEverywhere_ issues from git repositories
