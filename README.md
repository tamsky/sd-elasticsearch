SD-ElasticSearch
================

ElasticSearch plugin for ServerDensity.

Monitors the following statistics per node:

* CPU %
* Resident memory
* Shared memory
* Virtual memory
* Size on disk
* Number of docs

Graphs
------

You can split metrics into multiple graphs on the plugin tab (on your SD account). Each metric key comes with the node name prefixed. E.g. the keys for a node called `Firestar`:

* `Firestar - num docs`
* `Firestar - size (MiB)`
* `Firestar - virtual (MiB)`
* `Firestar - share (MiB)`
* `Firestar - cpu %`
* `Firestar - rss (MiB)`

![Sample graph](http://sd-plugins.s3.amazonaws.com/03/00ea05e2607206519d386e4778b4f2/ElasticSearch.19)

Installation
------------

Copy the `ElasticSearch.py` script to your `sd-agent` plugins folder e.g. `/usr/bin/sd-agent/plugins`. Create the plugins folder if it doesn't exist.

Configuration
-------------

Add your ES host to the ServerDensity configuration file e.g. `/etc/sd-agent/config.cfg)`:

```
[ElasticSearch]
host: localhost:9200
```

Make sure the agent knows where to find your plugins:

```
[Main]
plugin_directory: /usr/bin/sd-agent/plugins
```