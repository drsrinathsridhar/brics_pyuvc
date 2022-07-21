import numpy as np
import cv2
import threading
import time
import argparse
import sys
import os
FileDirPath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(FileDirPath, '..'))
import uvc
from sticradio.utilities import getCurrentEpochTime, makeCollage, StreamingMovingAverage

Parser = argparse.ArgumentParser(description='Sample script to stream from UVC cameras.')
Parser.add_argument('-i', '--id', help='Which camera IDs to use.', nargs='+', type=int, required=False, default=[])

def grab_frame(num):
    global Stop
    global FPS
    global lock
    global CapturedFrames
    while True:
        startTime = getCurrentEpochTime()
        Frame = Cams[num].get_frame_robust()
        lock.acquire()
        CapturedFrames[num] = np.copy(Frame.img)
        lock.release()
        # CapturedFrames[num] = Cams[num].get_frame()
        # print("Cam: {} shape: {}".format(num, CapturedFrames[num].img.shape))
        endTime = getCurrentEpochTime()
        ElapsedTime = (endTime - startTime)
        if ElapsedTime < 1000:
            time.sleep(0.001)  # Prevent CPU throttling
            ElapsedTime += 1000
        lock.acquire()
        CurrentFPS = 1e6 / (ElapsedTime)
        FPS[num] = FPSMovingAvg[num] + CurrentFPS
        lock.release()
        # print('FPS:', num, math.floor(FPS[num]), flush=True)

        if Stop:
            break

def display():
    global Stop
    global FPS
    global lock
    global CapturedFrames
    while True:
        lock.acquire()
        Collage = makeCollage(CapturedFrames, MaxWidth=1000, FPSList=FPS)
        # Collage = DummyFrame
        lock.release()
        cv2.imshow('Live Capture', Collage)
        Key = cv2.waitKey(1)
        if Key == 27:
            lock.acquire()
            Stop = True
            lock.release()
            break

if __name__ == '__main__':
    # if len(sys.argv) == 1:
    #     Parser.print_help()
    #     exit()
    Args = Parser.parse_args()

    dev_list = uvc.device_list()
    # random.shuffle(dev_list)
    nCams = len(dev_list)
    assert nCams > 0
    CamIdx = list(range(nCams))
    print('Found {} cameras with indices: {}.'.format(nCams, CamIdx))
    if Args.id != []:
        CamIdx = Args.id
    print('Limiting to camera indices: {}'.format(CamIdx))
    nCams = len(CamIdx)
    Cams = []
    for i in CamIdx:
        Cams.append(uvc.Capture(dev_list[i]["uid"]))
        controls_dict = dict([(c.display_name, c) for c in Cams[-1].controls])
        print('Camera in Bus:ID -', dev_list[i]['uid'], 'supports the following modes:', Cams[-1].avaible_modes)
        for Key in dev_list[i].keys():
            print(Key + ':', dev_list[i][Key])
        Cams[-1].frame_mode = Cams[-1].available_modes[0]
        print('Original camera bandwidth factor:', Cams[-1].bandwidth_factor)
        Cams[-1].bandwidth_factor = 0.5
        print('New camera bandwidth factor:', Cams[-1].bandwidth_factor)

    DummyFrame = np.zeros((Cams[0].frame_mode[1], Cams[0].frame_mode[0], 3))
    CapturedFrames = [DummyFrame]*nCams
    Stop = False
    FPS = [0]*nCams
    WindowSize = 200
    FPSMovingAvg = [StreamingMovingAverage(window_size=WindowSize)]*nCams
    lock = threading.Lock()
    Threads = []
    DispThread = threading.Thread(target=display)
    for i in range(nCams):
        Threads.append(threading.Thread(target=grab_frame, args=(i,)))

    DispThread.start()
    for i in range(nCams):
        Threads[i].start()

    DispThread.join()
    for i in range(nCams):
        Threads[i].join()
