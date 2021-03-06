:date: 2011-03-23

.. _manticore-ext-changes:

============================
Manticore extensions CHANGES
============================

.. include:: manticore-links.rst

2014-04-19 0.2.1
================
enhance gource extension:
- use VideoAudioMixer in postprocessing step to properly truncate
  duration of the final artifact to maximum video length
- add --time-lapse option to render shorter videos

2014-04-19 0.2.0
================
enhance gource extension:
- add --audio-source commandline option to provide background audio
- fix ffmpeg command after upgrading to ffmpeg-2.2.1

2013-11-03 0.1.5
================
- statistics fix: add newline after "all-git" in rst index file

2013-11-03 0.1.4
================
- statistics fix: include link to "all-git" in rst index file

2013-08-26 0.1.3
================
- minor fixes and enhancements

2013-08-25 0.1.2
================
- ``zt.manticore.ext.changes``: search for CHANGES.rst on top and second directory level of repository tree

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
