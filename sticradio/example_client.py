import sticradio

if __name__ == '__main__':
    Client = sticradio.STICRadioClient(hostname='localhost', port='8875')
    Client.start()
    Client.stop()