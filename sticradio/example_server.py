import sticradio
import argparse
import sys

Parser = argparse.ArgumentParser(description='Example script to create a websocket ping/pong server.')
Parser.add_argument('-p', '--port', help='Port number on host.', type=str, default='8181')

if __name__ == '__main__':
    Args = Parser.parse_args()

    Server = sticradio.STICRadioServer(port=Args.port)
    Server.start()