from __future__ import print_function

import random
import numpy as np
import uvc
import logging
import cv2
import threading
import time
import math
from datetime import datetime
import argparse, sys

Parser = argparse.ArgumentParser(description='Sample script to stream from UVC cameras.')
Parser.add_argument('-i', '--id', help='Which camera IDs to use.', nargs='+', type=int, required=False, default=[])

def getCurrentEpochTime():
    return int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() * 1e6)

def makeCollage(ImageList, MaxWidth=800, FPSList=[]):
    if ImageList is None:
        return None

    nImages = len(ImageList)
    if nImages == 0:
        return None
    if nImages == 1:
        return ImageList[0]

    # Assuming images are all same size or we will resize to same size as the first image
    Shape = ImageList[0].shape
    for Ctr, Image in enumerate(ImageList, 0):
        if len(FPSList) == len(ImageList):
            cv2.putText(img=Image, text=str(math.floor(FPSList[Ctr])), org=(Image.shape[1]-math.floor(Image.shape[1]/20), math.floor(Image.shape[1]/25)),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1.0, color=(0, 0, 255), thickness=2)
        if Shape[0] != Image.shape[0] or Shape[1] != Image.shape[1]:
            Image = cv2.resize(Image, Shape)

    nCols = math.ceil(math.sqrt(nImages))
    nRows = math.ceil(nImages / nCols)
    # print('nImages, Cols, Rows:', nImages, ',' ,nCols, ',', nRows)

    Collage = np.zeros((Shape[0]*nRows, Shape[1]*nCols, Shape[2]), np.uint8)
    for i in range(0, nImages):
        Row = math.floor(i / nCols)
        Col = i % nCols
        Collage[Row*Shape[0]:Row*Shape[0]+Shape[0], Col*Shape[1]:Col*Shape[1]+Shape[1], :] = ImageList[i].copy()

    if Collage.shape[1] > MaxWidth:
        Fact = Collage.shape[1] / MaxWidth
        NewHeight = round(Collage.shape[0] / Fact)
        Collage = cv2.resize(Collage, (MaxWidth, NewHeight))

    return Collage


if __name__ == '__main__':
    # if len(sys.argv) == 1:
    #     Parser.print_help()
    #     exit()
    Args = Parser.parse_args()

    logging.basicConfig(level=logging.INFO)

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
        Cams[-1].frame_mode = Cams[-1].avaible_modes[-1]
        Cams[-1].bandwidth_factor = 2
        # time.sleep(1.0)

    print(len(Cams))
    DummyFrame = np.zeros((Cams[0].frame_mode[1], Cams[0].frame_mode[0], 3))
    CapturedFrames = [DummyFrame]*nCams
    Stop = False
    FPS = [0]*nCams
    lock = threading.Lock()
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
            FPS[num] = 1e6 / (ElapsedTime)
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
            Collage = makeCollage(CapturedFrames, MaxWidth=800, FPSList=FPS)
            # Collage = DummyFrame
            lock.release()
            cv2.imshow('Live Capture', Collage)
            Key = cv2.waitKey(1)
            if Key == 27:
                lock.acquire()
                Stop = True
                lock.release()
                break

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
