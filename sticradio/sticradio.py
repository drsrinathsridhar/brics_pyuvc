import asyncio
import websockets
import utilities as utils
import time
import numpy as np
import struct
import cv2

class STICRadioServer():
    def __init__(self, port='80'):
        self.init(port)

    def init(self, port):
        self.Port = port
        self.TestData = np.random.rand(1920, 1080, 3)  # Simulating a full HD image

    async def event_loop(self, websocket, path):
        async for Data in websocket:
            (EpochTime, ImagePayload) = struct.unpack('Qs', Data)
            print('Data received from websocket:', EpochTime)
            self.TestData = np.frombuffer(ImagePayload, dtype=np.uint8)
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
        self.init(hostname, port)

    def init(self, hostname='localhost', port='80'):
        self.Hostname = hostname
        self.Port = port
        self.URI = 'ws://' + self.Hostname + ':' + self.Port
        self.Websocket = None
        self.Terminate = False
        self.ReceivedData = None
        # self.TestData = np.zeros((1920, 1080, 3), dtype=np.uint8) # Simulating a full HD image
        self.TestData = np.random.uniform(low=0.0, high= 255.0, size=(1920, 1080, 3)).astype(np.uint8)  # Simulating a full HD image

    async def send(self, data):
        await self.Websocket.send(data)

    async def recv(self):
        data = await self.Websocket.recv()
        return data

    async def event_loop(self):
        async with websockets.connect(self.URI) as websocket:
            print('[ INFO ]: Successfully connected to websocket server at', self.URI)
            while True:
                time.sleep(0.001)
                ImageBytes = self.TestData.tobytes()
                EpochTime = utils.getCurrentEpochTime()
                SendData = struct.pack('Qs', EpochTime, ImageBytes)
                # print('Sending Data:', EpochTime)
                # await websocket.send(str(EpochTime))
                await websocket.send(SendData)
                self.ReceivedData = await websocket.recv()
                # print('Received Data:', self.ReceivedData)
                print('Latency: {} milliseconds'.format((utils.getCurrentEpochTime() - int(self.ReceivedData))/2000))

    def start(self):
        print('[ INFO ]: Starting client...')
        asyncio.run(self.event_loop())

    def stop(self):
        self.Terminate = True
