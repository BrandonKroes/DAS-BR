import datetime
import os
import subprocess
import time

from common.communication.endpoint_config import EndpointConfig
from common.packets.blender_render_packet import BlenderRenderPacket
from common.packets.cluster_notify_packet import ClusterNotifyPacket
from common.packets.job_type import JobType
from common.packets.new_job_packet import NewJobPacket


class ClusterNotifyOperation:
    job_type = JobType.OPERATION
    operation_id = 0
    finished = False
    packets = []
    orchestrated = False

    def __init__(self, operation_id, data_packet):
        self.total_time = None
        self.operation_id = operation_id
        self.to_avoid_list = data_packet

    def orchestrate_cluster(self, master):
        for i in range(len(master.nodes)):
            if master.nodes[i] not in self.to_avoid_list:
                brp = ClusterNotifyPacket(i, job_type=JobType.STATUS,
                                          data_packet=master.nodes)
                ec = EndpointConfig(host=master.nodes[i][0]['worker']['host'],
                                    port=master.nodes[i][0]['worker']['port'],
                                    packet=brp)
                self.packets.append(ec)
        self.orchestrated = True

    def node_failure(self, master, failure_node):
        pass

    def get_packets(self):
        t_packet = self.packets
        self.finished = True
        return t_packet

    def process_progress_packet(self, received_packet):
        pass

    def print(self):
        print(self.__dict__)

    def on_cluster_complete(self):
        pass
