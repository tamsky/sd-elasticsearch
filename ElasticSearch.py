#!/usr/bin/env python
'''
ISC style license
http://www.openbsd.org/cgi-bin/cvsweb/~checkout~/src/share/misc/license.template?rev=HEAD
---
Copyright (c) 2011, 2012 Curve <justin@curvehq.com>

Permission to use, copy, modify, and distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
'''

import httplib
import json

class ElasticSearch:
    def __init__(self, agentConfig, checksLogger, rawConfig):
        self.agentConfig = agentConfig
        self.checksLogger = checksLogger
        self.rawConfig = rawConfig

        if self.agentConfig is None:
            self.setDefaultConfig()

        if ('ElasticSearch' not in self.agentConfig):
            self.setDefaultConfig()

    def setDefaultConfig(self):
        self.agentConfig = {}
        self.agentConfig['ElasticSearch'] = {'host': 'localhost:9200'}

    def getClusterInfo(self):
        conn = httplib.HTTPConnection(self.agentConfig['ElasticSearch']['host'])
        conn.request("GET", "/_cluster/nodes/stats?&all=true")
        return conn.getresponse().read()

    def process_data(self):
        #
        # Cluster nodes stats
        #
        response = self.getClusterInfo()
        stats = json.loads(response)

        one_megabyte_in_bytes = 1048576
        sd_data = {}
        for node in stats['nodes'].keys():
            name = stats['nodes'][node]['name']

            # Process CPU & Memory
            sd_data[name + ' - cpu %']            = stats['nodes'][node]['process']['cpu']['percent']
            sd_data[name + ' - rss (MiB)']        = stats['nodes'][node]['process']['mem']['resident_in_bytes'] / one_megabyte_in_bytes
            sd_data[name + ' - share (MiB)']      = stats['nodes'][node]['process']['mem']['share_in_bytes']  / one_megabyte_in_bytes
            sd_data[name + ' - virtual (MiB)']    = stats['nodes'][node]['process']['mem']['total_virtual_in_bytes']  / one_megabyte_in_bytes

            # Size on disk
            sd_data[name + ' - size (MiB)'] = stats['nodes'][node]['indices']['store']['size_in_bytes'] / one_megabyte_in_bytes

            # Doc count
            sd_data[name + ' - num docs'] = stats['nodes'][node]['indices']['docs']['count']

        return sd_data

    def run(self):
        metrics = self.process_data()
        return metrics

if __name__ == '__main__':
    es = ElasticSearch(None, None, None)
    print es.run()
