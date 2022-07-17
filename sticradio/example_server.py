import sticradio

if __name__ == '__main__':
    Server = sticradio.STICRadioServer(port='8080')
    Server.start()