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

Parser = argparse.ArgumentParser(description='Single camera image server.')
Parser.add_argument('-p', '--port', help='Port number on host.', type=str, default='8080')

class SingleCamServer(sr.STICRadioServer):
    def __init__(self, port='8080'):
        super().__init__(port)
        self.init()

    def init(self):
        self.ImagePayload = np.zeros((1280, 720, 3))
        self.Lock = threading.Lock()
        self.Stop = False
        self.FPS = 0
        WindowSize = 200
        self.FPSMovingAvg = StreamingMovingAverage(window_size=WindowSize)
        self.DispThread = threading.Thread(target=self.display)

    def display(self):
        print('Starting display thread...')
        while True:
            self.Lock.acquire()
            Collage = makeCollage([self.ImagePayload], MaxWidth=1000, FPSList=[self.FPS])
            self.Lock.release()
            cv2.imshow('Single Cam Server', Collage)
            Key = cv2.waitKey(1)
            if Key == 27:
                self.Lock.acquire()
                self.Stop = True
                asyncio.get_event_loop().stop()
                self.Lock.release()
                break

    async def event_loop(self, websocket, path):
        self.DispThread.start()
        async for Data in websocket:
            (EpochTime, ImagePayload) = struct.unpack('Qs', Data)
            print('Data received from websocket:', EpochTime)
            self.ImagePayload = np.frombuffer(ImagePayload, dtype=np.uint8)
            await websocket.send(str(EpochTime)) # Send only the epoch time back

# class SingleCamClient(sr.STICRadioClient):
#     def init(self):
#         dev_list = uvc.device_list()
#         # random.shuffle(dev_list)
#         nCams = len(dev_list)
#         assert nCams > 0
#         CamIdx = list(range(nCams))
#         assert Args.id in CamIdx
#         print('Found {} cameras with indices: {}. Using index {}'.format(nCams, CamIdx, Args.id))
#         Cam = uvc.Capture(dev_list[Args.id]["uid"])
#         # controls_dict = dict([(c.display_name, c) for c in Cam.controls])
#         print('Camera in Bus:ID -', dev_list[Args.id]['uid'], 'supports the following modes:', Cam.available_modes)
#         for Key in dev_list[Args.id].keys():
#             print(Key + ':', dev_list[Args.id][Key])
#         Cam.frame_mode = Cam.available_modes[0]
#         print('Original camera bandwidth factor:', Cam.bandwidth_factor)
#         Cam.bandwidth_factor = 0.5
#         print('New camera bandwidth factor:', Cam.bandwidth_factor)
#
#         self.ImagePayload = np.zeros((Cam.frame_mode[1], Cam.frame_mode[0], 3))

if __name__ == '__main__':
    # if len(sys.argv) == 1:
    #     Parser.print_help()
    #     exit()
    Args = Parser.parse_args()

    CamServer = SingleCamServer(Args.port)
    CamServer.start()