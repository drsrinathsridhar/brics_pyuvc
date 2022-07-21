import asyncio
import websockets
import time
import numpy as np
import struct
import sys
import os
FileDirPath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(FileDirPath, '.'))
import utilities as utils

class STICRadioServer():
    def __init__(self, port='8080'):
        self.Port = port
        self.init()

    def init(self):
        self.TestPayload = np.random.rand(1920, 1080, 3)  # Simulating a full HD image payload

    async def event_loop(self, websocket, path):
        async for Data in websocket:
            (EpochTime, ImagePayload) = struct.unpack('Qs', Data)
            print('Data received from websocket:', EpochTime)
            self.TestPayload = np.frombuffer(ImagePayload, dtype=np.uint8)
            await websocket.send(str(EpochTime)) # Send only the epoch time back

    async def main(self):
        async with websockets.serve(self.event_loop, port=self.Port):
            print('[ INFO ]: Successfully created websocket server in port', self.Port)
            await asyncio.Future()  # run forever

    def start(self):
        print('[ INFO ]: Starting server...')
        asyncio.run(self.main())

class STICRadioClient():
    def __init__(self, hostname, port):
        self.Hostname = hostname
        self.Port = port
        self.URI = 'ws://' + self.Hostname + ':' + self.Port
        self.Websocket = None
        self.init()

    def init(self):
        self.ReceivedData = None
        # self.TestData = np.zeros((1920, 1080, 3), dtype=np.uint8) # Simulating a full HD image
        self.TestData = np.random.uniform(low=0.0, high= 255.0, size=(1920, 1080, 3)).astype(np.uint8)  # Simulating a full HD image

    async def event_loop(self):
        async with websockets.connect(self.URI) as websocket:
            print('[ INFO ]: Successfully connected to websocket server at', self.URI)
            while True:
                time.sleep(1/260.0)
                ImageBytes = self.TestData.tobytes()
                EpochTime = utils.getCurrentEpochTime()
                SendData = struct.pack('Qs', EpochTime, ImageBytes)
                # print('Sending data at:', EpochTime)
                await websocket.send(SendData)
                self.ReceivedData = await websocket.recv()
                # print('Received Data:', self.ReceivedData)
                print('Latency: {} milliseconds'.format((utils.getCurrentEpochTime() - int(self.ReceivedData))/2000))

    def start(self):
        print('[ INFO ]: Starting client...')
        asyncio.run(self.event_loop())
