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
import asyncio

Parser = argparse.ArgumentParser(description='Single camera image server.')
Parser.add_argument('-p', '--port', help='Port number on this host.', required=True, type=str, default='8080')

class SingleCamServer(sr.STICRadioServer):
    def __init__(self, port='8080'):
        super().__init__(port)
        self.init()

    def init(self):
        self.FrameCaptureTime = 0
        self.ImagePayload = None
        self.JPEGBuffer = None
        self.Lock = threading.Lock()
        self.Stop = False
        self.FPS = 0
        self.TicToc = [0]*2
        WindowSize = 200
        self.FPSMovingAvg = StreamingMovingAverage(window_size=WindowSize)
        self.DispThread = threading.Thread(target=self.display)

    def display(self):
        print('Starting display thread...')
        while True:
            if self.JPEGBuffer is None:
                self.ImagePayload = np.zeros((720, 1280, 3))
            else:
                ImageArray = np.array(bytearray(self.JPEGBuffer), dtype=np.uint8)
                self.ImagePayload = cv2.imdecode(ImageArray, -1)

            if len(self.ImagePayload.shape) < 3:
                continue
            Collage = makeCollage([self.ImagePayload], MaxWidth=1000, FPSList=[self.FPS])
            cv2.imshow('Single Cam Server', Collage)
            Key = cv2.waitKey(1)
            if Key == 27:
                print('Stopping display...')
                self.Stop = True
                break

    async def event_loop(self, websocket, path):
        self.DispThread.start()
        async for Data in websocket:
            self.FrameCaptureTime = int.from_bytes(Data[:24], 'big')
            self.JPEGBuffer = Data[24:]
            await websocket.send(str(self.FrameCaptureTime)) # Send only the epoch time back for latency calculation

            self.TicToc[0] = self.TicToc[1]
            self.TicToc[1] = getCurrentEpochTime()
            ElapsedTime = (self.TicToc[1] - self.TicToc[0])
            CurrentFPS = 1e6 / (ElapsedTime)
            self.FPS = self.FPSMovingAvg + CurrentFPS


if __name__ == '__main__':
    if len(sys.argv) == 1:
        Parser.print_help()
        exit()
    Args = Parser.parse_args()

    CamServer = SingleCamServer(Args.port)
    CamServer.start()