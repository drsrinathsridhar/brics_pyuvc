import numpy as np
import cv2
import threading
import time
import argparse
import sys
import os
FileDirPath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(FileDirPath, '..'))
import uvc
from sticradio.utilities import getCurrentEpochTime, makeCollage, StreamingMovingAverage
from sticradio import sticradio as sr
import struct
import asyncio
import websockets

Parser = argparse.ArgumentParser(description='Example script to connect to a websocket ping/pong server.')
Parser.add_argument('-o', '--hostname', help='Hostname or IP address.', type=str, default='localhost')
Parser.add_argument('-p', '--port', help='Port number on host.', type=str, default='8875')
Parser.add_argument('-i', '--id', help='Which camera ID to use.', type=int, required=False, default=0)

class SingleCamClient(sr.STICRadioClient):
    def __init__(self, Args):
        self.Args = Args
        super().__init__(Args.hostname, Args.port)
        self.init()

    def init(self):
        self.Lock = threading.Lock()
        self.FPS = 0
        self.Latency = 0
        self.Stop = False
        WindowSize = 200
        self.FPSMovingAvg = StreamingMovingAverage(window_size=WindowSize)

        dev_list = uvc.device_list()
        # random.shuffle(dev_list)
        self.nCams = len(dev_list)
        assert self.nCams > 0
        CamIdx = list(range(self.nCams))
        assert self.Args.id in CamIdx
        print('Found {} cameras with indices: {}. Using camera with index {}.'.format(self.nCams, CamIdx, self.Args.id))
        self.Cam = uvc.Capture(dev_list[self.Args.id]['uid'])
        # controls_dict = dict([(c.display_name, c) for c in Cam.controls])
        print('Camera in Bus:ID -', dev_list[self.Args.id]['uid'], 'supports the following modes:', self.Cam.available_modes)
        for Key in dev_list[self.Args.id].keys():
            print(Key + ':', dev_list[self.Args.id][Key])
        self.Cam.frame_mode = self.Cam.available_modes[0]
        print('Original camera bandwidth factor:', self.Cam.bandwidth_factor)
        self.Cam.bandwidth_factor = 0.5
        print('New camera bandwidth factor:', self.Cam.bandwidth_factor)

        self.ImagePayload = np.zeros((self.Cam.frame_mode[1], self.Cam.frame_mode[0], 3))

    async def event_loop(self):
        async with websockets.connect(self.URI) as websocket:
            print('[ INFO ]: Successfully connected to websocket server at', self.URI)

            while True:
                startTime = getCurrentEpochTime()
                Frame = self.Cam.get_frame_robust()
                ImageBytes = Frame.tobytes()
                SendData = struct.pack('Qs', startTime, ImageBytes)
                # print('Sending data at:', startTime)
                await websocket.send(SendData)
                ReceivedData = await websocket.recv()
                # print('Received Data:', ReceivedData)
                self.Latency = (getCurrentEpochTime() - int(ReceivedData))/2000
                print('Latency: {} milliseconds'.format(self.Latency))

                self.Lock.acquire()
                self.ImagePayload = np.copy(Frame.img)
                self.Lock.release()
                # CapturedFrames[num] = Cams[num].get_frame()
                # print("Cam: {} shape: {}".format(num, CapturedFrames[num].img.shape))
                endTime = getCurrentEpochTime()
                ElapsedTime = (endTime - startTime)
                if ElapsedTime < 1000:
                    time.sleep(0.001)  # Prevent CPU throttling
                    ElapsedTime += 1000
                self.Lock.acquire()
                CurrentFPS = 1e6 / (ElapsedTime)
                self.FPS = self.FPSMovingAvg + CurrentFPS
                self.Lock.release()
                # print('FPS:', num, math.floor(FPS[num]), flush=True)

                if self.Stop:
                    break


if __name__ == '__main__':
    # if len(sys.argv) == 1:
    #     Parser.print_help()
    #     exit()
    Args = Parser.parse_args()

    CamServer = SingleCamClient(Args)
    CamServer.start()