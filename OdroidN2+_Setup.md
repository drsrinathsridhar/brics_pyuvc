TODO: create an image

Burn Ubuntu MATE image on SD card

`sudo apt install build-essential libusb-1.0-0-dev cmake`

Follow instructions on STIC.md to install libuvc, pyuvc, python, opencv, etc.

For Python install miniforge (https://github.com/conda-forge/miniforge)

On Odroid Ubuntu MATE, the udev rules are a bit different:

`echo 'SUBSYSTEM=="usb",  ENV{DEVTYPE}=="usb_device", GROUP="odroid", MODE="0666"' | sudo tee /etc/udev/rules.d/10-libuvc.rules > /dev/null`

Update is also different

`sudo udevadm control --reload-rules && udevadm trigger`


Create a disk image from a working SD card:

`sudo dd bs=4M if=/dev/sda of=~/2020-07-30_Odroid.img status=progress`
