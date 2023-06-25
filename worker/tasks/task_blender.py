import subprocess
import sys
import os.path
import sys
import os.path

from common.communication import EndpointConfig

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from worker.tasks import AbstractTask


class TaskBlender(AbstractTask):
    conf = {  # items to copy
        'blender_path': "unset",
        'blender_file_path': 'unset',
        'start_frame': 'unset',
        'stop_frame': 'unset',
        'engine': 'unset',
        'cycles_device': 'undefined',
        'job_id': 'undefined',
        'output_folder': 'unset',
        'operation_reference': 'unset',
    }
    finished = False
    running = False
    init = False
    progress = 0
    render_process = None

    def __init__(self, **kwargs):
        # read config to override at run time.
        super().__init__(**kwargs)
        self.blender_path = None
        self.cycles_device = None
        self.start_frame = None
        self.blender_file_path = None
        self.engine = None
        self.stop_frame = None
        self.output_folder = None
        self.worker = None
        self.frame_progress = False
        self.frame_count = 0
        self.first_frame = True

        for key, val in self.conf.items():
            self.__dict__[key] = kwargs.get(key, val)

    def is_finished(self):
        return self.finished

    def execute(self, worker):
        if 'unset' in self.__dict__:
            return print("Unset value is supplied. blender_file_path, start_frame, stop_frame and engine are mandatory")

        extra_args = []
        if self.engine == "CYCLES" and self.cycles_device != "undefined":
            extra_args = [" -- --cycles-device " + self.cycles_device]

        args = [
            ' --background',  # Setting Blender to background/headless config
            self.blender_file_path,
            '--engine', self.engine,
            '--frame-start', str(self.start_frame),
            '--frame-end', str(self.stop_frame),
            '--render-output', str(self.output_folder)
        ]
        extra_args = [' -a'] + extra_args  # Render the whole animation using all the settings saved in the blend-file.
        self.running = True
        self.render_process = subprocess
        running_process = self.render_process.Popen([self.blender_path + " ".join(args) + " ".join(extra_args)],
                                                    shell=True,
                                                    stdout=subprocess.PIPE, bufsize=1)
        while running_process.poll() is None:
            line = running_process.stdout.readline()
            self.process_line(line.decode("utf-8"))
            if self.first_frame:
                self.frame_progress = False
                self.first_frame = False
            elif self.frame_progress is True:
                self.frame_progress = False
                from common.packets import JobType
                from common.packets import PrintPacket
                worker.send_packet(
                    EndpointConfig(host=worker.master_host, port=worker.master_port,
                                   packet=PrintPacket(packet_id=1, job_type=JobType.OPERATION,
                                                      data_packet={'operation_reference': self.operation_reference,
                                                                   'worker_id': worker.worker_id,
                                                                   'packet_reference': self.frame_count})))
            self.finished = True

    def process_line(self, line):
        # Example line: Fra:1 Mem:163.57M (Peak 163.59M)
        # search for digit
        if len(line) > 10:
            buffer = ""

            prepend = line[0:4]

            if prepend == "Fra:":  # if it is a frame
                for c in line[4:-1]:
                    from curses.ascii import isdigit
                    if isdigit(c):
                        buffer += c
                    else:
                        break

                if self.frame_count < int(buffer):
                    self.frame_progress = True
                    self.frame_count = int(buffer)

    def render_status(self):
        if self.init:
            return "Starting blender render."
        return "At frame %1 from the %2. Using Engine %3".format(str(self.progress), str(self.stop_frame),
                                                                 self.engine)

    @staticmethod
    def is_capable():
        return True
