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
import logging as log

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

    def _get(self, path):
        conn = httplib.HTTPConnection(self.agentConfig['ElasticSearch']['host'])
        conn.request("GET", path)
        result = conn.getresponse().read()
        return json.loads(result)

    def getClusterStats(self):
        return self._get("/_cluster/stats?pretty")

    def getClusterHealth(self):
        return self._get("/_cluster/health?pretty")

    def getNodeId(self):
        nodeInfo = self._get("/_nodes/_local/id")
        return nodeInfo['nodes'].keys()[0]

    def getNodeStats(self, id):
#        return self._get("/_nodes/_local/stats")['nodes'][id]
        return self._get("/_nodes/" + id + "/stats")['nodes'][id]

    def process_data(self):
        #
        # Cluster nodes stats
        #
        one_megabyte_in_bytes = 1048576
        sd_data = {}

        try:
            clusterStats = self.getClusterStats()
            clusterHealth = self.getClusterHealth()
            nodeStats = self.getNodeStats(self.getNodeId())

        except Exception, e:
            return {
                'cluster_status': 2
            }

        # log.info("nodeStats")
        # log.info(json.dumps(nodeStats))

        if clusterStats['status'] == 'green':
            clusterStats['status'] = 0
        elif clusterStatus['status'] == 'yellow':
            clusterStats['status'] = 1
        else:
            clusterStatus['status'] = 2

        # Cluster-wide state reporting (each node reports their view of this state)
        sd_data['cluster_status']     = clusterStats['status']
        sd_data['cluster_node_count'] = clusterStats['nodes']['count']['total']

        sd_data['cluster_memory_used (MiB)'] = clusterStats['nodes']['jvm']['mem']['heap_used_in_bytes'] / one_megabyte_in_bytes
        sd_data['cluster_relocating_shards'] = clusterHealth['relocating_shards']
        sd_data['cluster_unassigned_shards'] = clusterHealth['unassigned_shards']
            
        # ES data
        sd_data['num docs']                      = nodeStats['indices']['docs']['count']
        sd_data['indices merges total']          = nodeStats['indices']['merges']['total']
        sd_data['indices indexing delete total'] = nodeStats['indices']['indexing']['delete_total']
        sd_data['indices indexing index total']  = nodeStats['indices']['indexing']['index_total']
        sd_data['indices search fetch total']    = nodeStats['indices']['search']['fetch_total']
        sd_data['indices search query total']    = nodeStats['indices']['search']['query_total']
        sd_data['size (MiB)']                    = nodeStats['indices']['store']['size_in_bytes'] / one_megabyte_in_bytes

        # ES Binary state
        sd_data['open http connections']      = nodeStats['http']['current_open']


        # Process CPU & Memory
        sd_data['cpu %']                      = nodeStats['process']['cpu']['percent']
        sd_data['rss (MiB)']                  = nodeStats['process']['mem']['resident_in_bytes'] / one_megabyte_in_bytes
        sd_data['share (MiB)']                = nodeStats['process']['mem']['share_in_bytes']  / one_megabyte_in_bytes
        sd_data['virtual (MiB)']              = nodeStats['process']['mem']['total_virtual_in_bytes']  / one_megabyte_in_bytes

        sd_data['free mem %']                 = nodeStats['os']['mem']['free_percent']
        sd_data['used mem %']                 = nodeStats['os']['mem']['used_percent']
        sd_data['heap used %']                = nodeStats['jvm']['mem']['heap_used_percent']
        sd_data['thread count']               = nodeStats['jvm']['threads']['count']
        sd_data['thread count (peak)']        = nodeStats['jvm']['threads']['peak_count']
        sd_data['process uptime (seconds)']   = nodeStats['jvm']['uptime_in_millis'] / 1000

        # Network (apparently ES gathers from /proc/net/sockstat:)
        sd_data['tcp active opens']           = nodeStats['network']['tcp']['active_opens']
        sd_data['tcp attempt fails']          = nodeStats['network']['tcp']['attempt_fails']
        sd_data['tcp current established']    = nodeStats['network']['tcp']['curr_estab']
        sd_data['tcp established resets']     = nodeStats['network']['tcp']['estab_resets']
        sd_data['tcp in errors']              = nodeStats['network']['tcp']['in_errs']
        sd_data['tcp in segments']            = nodeStats['network']['tcp']['in_segs']
        sd_data['tcp out resets']             = nodeStats['network']['tcp']['out_rsts']
        sd_data['tcp out segments']           = nodeStats['network']['tcp']['out_segs']
        sd_data['tcp passive opens']          = nodeStats['network']['tcp']['passive_opens']
        sd_data['tcp retransmitted segments'] = nodeStats['network']['tcp']['retrans_segs']

        return sd_data

    def run(self):
        metrics = self.process_data()
        return metrics

if __name__ == '__main__':
    es = ElasticSearch(None, None, None)
    print es.run()
