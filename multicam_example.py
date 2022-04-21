from __future__ import print_function
import uvc
import logging
import cv2

logging.basicConfig(level=logging.INFO)

dev_list = uvc.device_list()
dev_list = [dev_list[0]]
print('Found {} cameras.'.format(len(dev_list)))
Cams = []
for i in range(len(dev_list)):
    Cams.append(uvc.Capture(dev_list[i]["uid"]))
    print('Supported modes:', Cams[i].avaible_modes)
    Cams[i].frame_mode = (640, 480, 60)

#exit()

# for x in range(10):
for i in range(len(dev_list)):
    frame = Cams[i].get_frame_robust()
    print(frame.img.shape)

# Uncomment the following lines to configure the Pupil 200Hz IR cameras:
# controls_dict = dict([(c.display_name, c) for c in cap.controls])
# controls_dict['Auto Exposure Mode'].value = 1
# controls_dict['Gamma'].value = 200

for i in range(len(dev_list)):
    Cams[i] = None

