import datetime
import os
import subprocess
import time

from common.communication.endpoint_config import EndpointConfig
from common.packets.blender_render_packet import BlenderRenderPacket
from common.packets.job_type import JobType
from common.packets.new_job_packet import NewJobPacket


class BlenderQueuedOperation:
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
    frames_to_render = []
    nodes = []
    outstanding_packets = []

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
        self.nodes = nodes
        frame_count = (self.stop_frame + 1) - self.start_frame

        for frame in range(frame_count):
            self.frames_to_render.append(frame + self.start_frame)

        for i in range(len(nodes)):
            front_queue = self.frames_to_render.pop(0)
            ec = EndpointConfig(host=nodes[i][0]['worker']['host'],
                                port=nodes[i][0]['worker']['port'],
                                packet=self.send_package(front_queue, i))
            self.packets.append(ec)

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
        default_node = master.nodes[0]
        node_info = default_node[0]

        # Redirecting the packet to a different node!
        to_be_redistributed.host = node_info['worker']['host']
        to_be_redistributed.port = node_info['worker']['port']

        master.send_packet(to_be_redistributed)
        packets.append(to_be_redistributed)
        self.packets = packets

    def get_packets(self):
        t_packet = self.packets
        return t_packet

    def process_progress_packet(self, received_packet):
        '''
        {'operation_reference': 1, 'packet_reference': 1, 'blender_file_path': '/home/batkroes/Forrest720P.blend', 'start_frame': 1, 'stop_frame': 1, 'output_folder': '/var/scratch/batkroes/Forrest720PQueued1/', 'engine': 'CYCLES', 'worker': 0}
        '''

        frames_completed = []
        backup_packet = []
        for packet in self.outstanding_packets:
            if packet.data_packet['packet_reference'] != received_packet['packet_reference']:
                backup_packet.append(packet)
        self.outstanding_packets = backup_packet
        self.packets = []

        if len(self.frames_to_render) > 0:
            pass
            front_queue = self.frames_to_render.pop(0)
            ec = EndpointConfig(host=self.nodes[received_packet['worker']][0]['worker']['host'],
                                port=self.nodes[received_packet['worker']][0]['worker']['port'],
                                packet=self.send_package(front_queue, received_packet['worker']))

            self.packets.append(ec)
        else:
            if 0 == len(self.frames_to_render) and 0 == len(self.packets) and 0 == len(self.outstanding_packets):
                self.finished = True
                self.on_cluster_complete()

    def send_package(self, frame, worker):

        brp = BlenderRenderPacket(frame, job_type=JobType.RENDER,
                                  data_packet={
                                      'operation_reference': self.operation_id,
                                      'packet_reference': frame,
                                      'blender_file_path': self.blender_file_path,
                                      'start_frame': frame,
                                      'stop_frame': frame,
                                      'output_folder': self.output_path + str(self.operation_id) + "/",
                                      'engine': self.engine,
                                      'worker': worker,
                                  })
        print(brp.__dict__)
        self.outstanding_packets.append(brp)
        return brp

    def print(self):
        print(self.__dict__)

    def on_cluster_complete(self):
        if self.finished:
            merge_command = "ffmpeg -nostdin -y -framerate " + str(
                self.frame_rate) + " -pattern_type glob -i '" + self.output_path + str(
                self.operation_id) + "/" + "*.png' -c:v libx264 -pix_fmt yuv420p " + self.output_path + str(
                self.operation_id) + "/" + str(
                self.operation_id) + ".mp4  "

            print(self.start_time.strftime("%d/%m/%Y %H:%M:%S"))
            self.end_time = datetime.datetime.now()
            print(self.end_time.strftime("%d/%m/%Y %H:%M:%S"))
            self.total_time = self.end_time - self.start_time
            print(self.total_time.total_seconds())
            print(merge_command)
            '''
            open(self.output_path + str(
                self.operation_id) + "/" + self.start_time.strftime("%H %M %S") + ".txt", "x")
            with open(self.output_path + str(
                    self.operation_id) + "/" + self.start_time.strftime("%H %M %S") + ".txt", "a") as file:
                file.write('start time: ' + self.start_time.strftime("%d/%m/%Y %H:%M:%S") + "\n")
                file.write('end time: ' + self.end_time.strftime("%d/%m/%Y %H:%M:%S") + "\n")
                file.write('duration: ' + str(self.total_time.total_seconds()) + "\n")
            '''
