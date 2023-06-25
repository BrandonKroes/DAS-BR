import datetime
import os
import subprocess
import time

from common.communication.endpoint_config import EndpointConfig
from common.packets.blender_render_packet import BlenderRenderPacket
from common.packets.job_type import JobType
from common.packets.new_job_packet import NewJobPacket


def get_scaled_division(frames, nodes):
    scaled_frames = []
    total_gpu_computation = 0
    for node in nodes:
        total_gpu_computation += node['benchmark_score']
    for node in nodes:
        import math
        scaled_frames[node['worker_id']] = math.floor(frames * (node['benchmark_score'] / total_gpu_computation))
    return scaled_frames


class BlenderScaledOperation:
    job_type = JobType.OPERATION
    operation_id = 0
    finished = False
    blender_file_path = ""
    start_frame = ""
    stop_frame = ""
    engine = ""
    capable_nodes = []
    packets = []
    orchestrated = False
    start_time = ""
    end_time = ""
    frame_rate = ""

    def __init__(self, operation_id, data_packet):
        self.total_time = None
        self.operation_id = operation_id
        self.blender_file_path = data_packet['blender_file_path']
        self.start_frame = data_packet['start_frame']
        self.stop_frame = data_packet['stop_frame']
        self.engine = data_packet['engine']
        self.frame_rate = data_packet['frame_rate']
        self.output_path = data_packet['output_path']

    def orchestrate_cluster(self, nodes):

        self.start_time = datetime.datetime.now()

        packet_id = 0
        frames = (self.stop_frame + 1) - self.start_frame
        frames_per_node = get_scaled_division(frames, nodes)

        offset = 0
        for i in range(len(nodes)):
            brp = BlenderRenderPacket(packet_id, job_type=JobType.RENDER,
                                      data_packet={
                                          'operation_reference': self.operation_id,
                                          'packet_reference': packet_id,
                                          'blender_file_path': self.blender_file_path,
                                          'start_frame': self.start_frame + offset,
                                          'stop_frame': self.start_frame + offset + frames_per_node[i] - 1,
                                          'output_folder': self.output_path + str(self.operation_id) + "/",
                                          'engine': self.engine
                                      })
            ec = EndpointConfig(host=nodes[i][0]['worker']['host'],
                                port=nodes[i][0]['worker']['port'],
                                packet=brp)
            self.packets.append(ec)
            packet_id += 1
            offset += frames_per_node[i]

        self.orchestrated = True

    def node_failure(self, master, failure_node):
        # check which jobs the node had
        to_be_redistributed: EndpointConfig = None
        packets = []
        for endpoint in self.packets:
            if endpoint.host == failure_node['worker']['host'] and endpoint.port == failure_node['worker']['port']:
                to_be_redistributed = endpoint
            else:
                packets.append(endpoint)

        if to_be_redistributed is None:
            # this operation had nothing to do with this task!
            return

        # TODO: Dynamically decide which node should be picked!
        default_node = master.nodes[0]
        node_info = default_node[0]

        # Redirecting the packet to a different node!
        to_be_redistributed.host = node_info['worker']['host']
        to_be_redistributed.port = node_info['worker']['port']

        master.send_packet(to_be_redistributed)
        packets.append(to_be_redistributed)
        self.packets = packets

    @staticmethod
    def get_evenly_divided_values(value_to_be_distributed, amount_divisions):
        return [(value_to_be_distributed // amount_divisions) + (
            1 if i < (value_to_be_distributed % amount_divisions) else 0) for i in range(amount_divisions)]

    def get_packets(self):
        t_packet = self.packets
        return t_packet

    def process_progress_packet(self, received_packet):
        backup_packet = []
        for packet in self.packets:
            print(received_packet)
            if packet.packet.data_packet['packet_reference'] != received_packet['packet_reference']:
                backup_packet.append(packet)
        self.packets = backup_packet

        if 0 == len(backup_packet):
            self.on_cluster_complete()

    def print(self):
        print(self.__dict__)

    def on_cluster_complete(self):

        merge_command = "ffmpeg -nostdin -y -framerate " + str(
            self.frame_rate) + " -pattern_type glob -i '" + self.output_path + str(
            self.operation_id) + "/" + "*.png' -c:v libx264 -pix_fmt yuv420p " + self.output_path + str(
            self.operation_id) + "/" + str(
            self.operation_id) + ".mp4  "
        print(merge_command)

        self.finished = True
        self.end_time = datetime.datetime.now()
        self.total_time = self.end_time - self.start_time

        open(self.output_path + str(
            self.operation_id) + "/" + self.start_time.strftime("%H %M %S") + ".txt", "x")
        with open(self.output_path + str(
                self.operation_id) + "/" + self.start_time.strftime("%H %M %S") + ".txt", "a") as file:
            file.write('start time: ' + self.start_time.strftime("%d/%m/%Y %H:%M:%S") + "\n")
            file.write('end time: ' + self.end_time.strftime("%d/%m/%Y %H:%M:%S") + "\n")
            file.write('duration: ' + str(self.total_time.total_seconds()) + "\n")
