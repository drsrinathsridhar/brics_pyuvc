import sticradio

if __name__ == '__main__':
    Server = sticradio.STICRadioServer(port='8875')
    Server.start()