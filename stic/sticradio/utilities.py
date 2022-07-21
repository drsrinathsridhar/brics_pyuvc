from datetime import datetime
import cv2
import math
import numpy as np

def getCurrentEpochTime():
    return int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() * 1e6)

def makeCollage(ImageList, MaxWidth=800, FPSList=[]):
    if ImageList is None:
        return None

    nImages = len(ImageList)
    if nImages == 0:
        return None

    # Assuming images are all same size or we will resize to same size as the first image
    Shape = ImageList[0].shape
    for Ctr, Image in enumerate(ImageList, 0):
        if len(FPSList) == len(ImageList):
            cv2.putText(img=Image, text=str(math.floor(FPSList[Ctr])), org=(Image.shape[1]-math.floor(Image.shape[1]/20), math.floor(Image.shape[1]/25)),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1.0, color=(0, 0, 255), thickness=2)
        if Shape[0] != Image.shape[0] or Shape[1] != Image.shape[1]:
            Image = cv2.resize(Image, Shape)

    if nImages > 1:
        nCols = math.ceil(math.sqrt(nImages))
        nRows = math.ceil(nImages / nCols)
        # print('nImages, Cols, Rows:', nImages, ',' ,nCols, ',', nRows)

        Collage = np.zeros((Shape[0]*nRows, Shape[1]*nCols, Shape[2]), np.uint8)
        for i in range(0, nImages):
            Row = math.floor(i / nCols)
            Col = i % nCols
            Collage[Row*Shape[0]:Row*Shape[0]+Shape[0], Col*Shape[1]:Col*Shape[1]+Shape[1], :] = ImageList[i].copy()
    else:
        Collage = ImageList[0]

    if Collage.shape[1] > MaxWidth:
        Fact = Collage.shape[1] / MaxWidth
        NewHeight = round(Collage.shape[0] / Fact)
        Collage = cv2.resize(Collage, (MaxWidth, NewHeight))

    return Collage

class StreamingMovingAverage():
    def __init__(self, window_size=100):
        self.window_size = window_size
        self.values = []
        self.sum = 0

    def __add__(self, value):
        self.values.append(value)
        self.sum += value
        if len(self.values) > self.window_size:
            self.sum -= self.values.pop(0)
        return float(self.sum) / len(self.values)

