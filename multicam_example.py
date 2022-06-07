from __future__ import print_function

import numpy as np
import uvc
import logging
import cv2
import threading
import time
import math
from datetime import datetime

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
    logging.basicConfig(level=logging.INFO)

    dev_list = uvc.device_list()
    # dev_list = [dev_list[0]]
    nCams = len(dev_list)
    print('Found {} cameras.'.format(nCams))
    nCams = 6
    print('WARNING: Limiting to {} cameras.'.format(nCams))
    Cams = []
    for i in range(nCams):
        Cams.append(uvc.Capture(dev_list[i]["uid"]))
        print('Supported modes:', Cams[i].avaible_modes)
        Cams[i].frame_mode = Cams[i].avaible_modes[1]
        Cams[i].bandwidth_factor = 0.9

    CapturedFrames = [None]*nCams
    DummyImage = np.empty((Cams[i].frame_mode[1], Cams[i].frame_mode[0], 3))
    Stop = False
    FPS = [0]*nCams
    lock = threading.Lock()
    def grab_frame(num):
        global Stop
        global FPS
        global lock
        while True:
            startTime = getCurrentEpochTime()
            CapturedFrames[num] = Cams[num].get_frame_robust()
            # print("Cam: {} shape: {}".format(num, CapturedFrames[num].img.shape))
            endTime = getCurrentEpochTime()
            ElapsedTime = (endTime - startTime)
            if ElapsedTime < 1000:
                time.sleep(0.001)  # Prevent CPU throttling
                ElapsedTime += 1000
            with lock:
                FPS[num] = 1e6 / (ElapsedTime)
            # print('FPS:', num, math.floor(FPS[num]), flush=True)

            if Stop:
                break

    def display():
        global Stop
        global FPS
        global lock
        while len(CapturedFrames) > 0:
            if CapturedFrames[0] is not None:
                with lock:
                    ImageList = []
                    for frame in CapturedFrames:
                        if frame is not None:
                            ImageList.append(frame.img)
                    Collage = makeCollage(ImageList, MaxWidth=1600, FPSList=FPS)
                cv2.imshow('Live Capture', Collage)
            else:
                cv2.imshow('Live Capture', DummyImage)
            Key = cv2.waitKey(1)
            if Key == 27:
                with lock:
                    Stop = True
                break

    Threads = []
    DispThread = threading.Thread(target=display)
    for i in range(nCams):
        Threads.append(threading.Thread(target=grab_frame, args=(i,)))
    for i in range(nCams):
        Threads[i].start()
    DispThread.start()
    DispThread.join()
    for i in range(nCams):
        Threads[i].join()

    for i in range(len(dev_list)):
        Cams[i] = None

