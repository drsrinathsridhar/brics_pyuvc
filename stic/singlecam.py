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

Parser = argparse.ArgumentParser(description='Sample script to stream from a single UVC camera.')
Parser.add_argument('-i', '--id', help='Which camera ID to use.', type=int, required=False, default=0)

def grab_frame():
    global Stop
    global FPS
    global FPSMovingAvg
    global lock
    global CapturedFrame
    global Cam
    while True:
        startTime = getCurrentEpochTime()
        Frame = Cam.get_frame_robust()
        lock.acquire()
        CapturedFrame = np.copy(Frame.img)
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
        FPS = FPSMovingAvg + CurrentFPS
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
        Collage = makeCollage([CapturedFrame], MaxWidth=1000, FPSList=[FPS])
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
    assert Args.id in CamIdx
    print('Found {} cameras with indices: {}. Using index {}'.format(nCams, CamIdx, Args.id))
    nCams = 1
    Cam = uvc.Capture(dev_list[Args.id]["uid"])
    controls_dict = dict([(c.display_name, c) for c in Cam.controls])
    print('Camera in Bus:ID -', dev_list[Args.id]['uid'], 'supports the following modes:', Cam.available_modes)
    for Key in dev_list[Args.id].keys():
        print(Key + ':', dev_list[Args.id][Key])
    Cam.frame_mode = Cam.available_modes[0]
    print('Original camera bandwidth factor:', Cam.bandwidth_factor)
    Cam.bandwidth_factor = 2
    print('New camera bandwidth factor:', Cam.bandwidth_factor)

    CapturedFrame = np.zeros((Cam.frame_mode[1], Cam.frame_mode[0], 3))
    Stop = False
    FPS = 0
    WindowSize = 200
    FPSMovingAvg = StreamingMovingAverage(window_size=WindowSize)
    lock = threading.Lock()
    Threads = []

    DispThread = threading.Thread(target=display)
    CaptureThread = threading.Thread(target=grab_frame)

    DispThread.start()
    CaptureThread.start()
    DispThread.join()
    CaptureThread.join()
