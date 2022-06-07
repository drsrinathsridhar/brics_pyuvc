from __future__ import print_function
import uvc
import logging
import cv2


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    dev_list = uvc.device_list()
    print(dev_list)
    cap = uvc.Capture(dev_list[0]["uid"])
    if cap is None:
        print('No compatible UVC devices found. Exiting.')
        exit()

    print('Available capture modes:', cap.available_modes)
    print('Device name:', cap.name)
    print('Bandwidth facto:', cap.bandwidth_factor)
    # Uncomment the following lines to configure the Pupil 200Hz IR cameras:
    controls_dict = dict([(c.display_name, c) for c in cap.controls])
    print('Camera Controls:', controls_dict)
    # controls_dict['Auto Exposure Mode'].value = 1
    # controls_dict['Gamma'].value = 200

    assert len(cap.available_modes) > 0

    cap.frame_mode = cap.available_modes[-1]
    print('Using capture mode:', cap.frame_mode)

    while True:
        frame = cap.get_frame_robust()
        # frame = cap.get_frame()
        # print(frame.img.shape)

        cv2.imshow('Live Capture',frame.img)
        Key = cv2.waitKey(1)
        if Key == 27:
            break
        if Key == ord('s'):
            cv2.imwrite('frame.png', frame.img)

    cap = None
