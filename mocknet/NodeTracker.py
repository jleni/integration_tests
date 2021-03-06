# coding=utf-8
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
import time
from queue import Empty


class NodeLogTracker(object):
    def __init__(self, mocknet):
        self.node_status = {}
        self.mocknet = mocknet

        self.abort_triggers = [
            "<_Rendezvous of RPC that terminated with (StatusCode.UNKNOWN",
            "Traceback (most recent call last):"
        ]

        self.abort_requested = False

    def synced_count(self):
        count = 0
        for k, v in self.node_status.items():
            if v == 'synced':
                count += 1
        return count

    def track(self, output=True):
        msg = ''
        try:
            msg = self.mocknet.log_queue.get(block=True, timeout=1)
            self.parse(msg)
            if output:
                print(msg, end='')

            for s in self.abort_triggers:
                if s in msg:
                    self.abort_requested = True

        except Empty:
            if self.abort_requested:
                raise Exception("ABORT TRIGGERED")

            time.sleep(0.05)

        return msg

    def parse(self, msg):
        parts = msg.split('|')
        if len(parts) > 4:
            node_id = parts[0].strip()
            status = parts[3].strip()
            self.node_status[node_id] = status

    def get_status(self, node_id):
        return self.node_status.get(node_id, 'unknown')
