# #!/usr/bin/env python
#
# import asyncio
# import websockets
#
#
# async def hello():
#     print('Running client...')
#     async with websockets.connect("ws://localhost:8765") as websocket:
#         Message = 'Hello world!'
#         print(Message)
#         await websocket.send(Message)
#         await websocket.recv()
#
#
# asyncio.run(hello())

import sticradio
import argparse

Parser = argparse.ArgumentParser(description='Example script to connect to a websocket ping/pong server.')
Parser.add_argument('-o', '--hostname', help='Hostname or IP address.', type=str, default='localhost')
Parser.add_argument('-p', '--port', help='Port number on host.', type=str, default='8875')

if __name__ == '__main__':
    Args = Parser.parse_args()

    Client = sticradio.STICRadioClient(hostname=Args.hostname, port=Args.port)
    Client.start()
