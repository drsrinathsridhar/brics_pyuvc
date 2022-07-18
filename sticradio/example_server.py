# import asyncio
# import websockets
#
# async def echo(websocket):
#     async for message in websocket:
#         print(message)
#         await websocket.send(message)
#
# async def main():
#     print('Running server...')
#     async with websockets.serve(echo, "localhost", 8765):
#         await asyncio.Future()  # run forever
#
# asyncio.run(main())

import sticradio
import argparse
import sys

Parser = argparse.ArgumentParser(description='Example script to create a websocket ping/pong server.')
Parser.add_argument('-p', '--port', help='Port number on host.', type=str, default='8181')

if __name__ == '__main__':
    Args = Parser.parse_args()

    Server = sticradio.STICRadioServer(port=Args.port)
    Server.start()