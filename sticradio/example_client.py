import sticradio
import argparse
import sys

Parser = argparse.ArgumentParser(description='Example script to connect to a websocket ping/pong server.')
Parser.add_argument('-o', '--hostname', help='Hostname or IP address.', type=str, default='localhost')
Parser.add_argument('-p', '--port', help='Port number on host.', type=str, default='8875')

if __name__ == '__main__':
    # if len(sys.argv) >= 1:
    #     Parser.print_help()
    #     exit()
    Args = Parser.parse_args()

    Client = sticradio.STICRadioClient(hostname=Args.hostname, port=Args.port)
    Client.start()
