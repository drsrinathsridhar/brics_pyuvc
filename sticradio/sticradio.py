import asyncio
import websockets
import utilities as utils
import time

class STICRadioServer():
    def __init__(self, port='80'):
        self.init(port)

    def init(self, port):
        self.Port = port
        self.WSServer = None
        self.create()

    def create(self):
        self.WSServer = websockets.serve(self.event_loop, 'localhost', self.Port)
        print('[ INFO ]: Successfully created websocket server in port', self.Port)

    async def event_loop(self, websocket, path):
        async for Data in websocket:
            print('Data received from websocket:', Data)
            await websocket.send(Data) # Send the data back

    def start(self):
        print('[ INFO ]: Starting server...')
        asyncio.get_event_loop().run_until_complete(self.WSServer)
        asyncio.get_event_loop().run_forever()


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

    async def send(self, data):
        await self.Websocket.send(data)

    async def recv(self):
        data = await self.Websocket.recv()
        return data

    async def event_loop(self):
        async with websockets.connect(self.URI) as websocket:
            print('[ INFO ]: Successfully connected to websocket server at', self.URI)
            while True:
                time.sleep(1)
                EpochTime = utils.getCurrentEpochTime()
                print('Sending Data:', EpochTime)
                await websocket.send(str(EpochTime))
                self.ReceivedData = await websocket.recv()
                print('Received Data:', self.ReceivedData)
                print('Latency: {} milliseconds'.format((utils.getCurrentEpochTime() - int(self.ReceivedData))/2000))

    def start(self):
        print('[ INFO ]: Starting client...')
        asyncio.get_event_loop().run_until_complete(self.event_loop())

    def stop(self):
        self.Terminate = True
