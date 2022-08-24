pyuvc_brics
============

`pyuvc_brics` is a fork of [pupil-labs/pyuvc](https://github.com/pupil-labs/pyuvc) specifically modified for the (BRICS)[https://github.com/brown-ivl/brics] project. * Only Ubunutu is supported for now*.

`pyuvc` is a set of Python bindings for the Pupil Labs fork of [libuvc](https://github.com/pupil-labs/libuvc) with super fast jpeg decompression using [libjpegturbo](http://libjpeg-turbo.virtualgl.org/) (utilizing the tubojpeg api).

* cross platform access to UVC capture devices.
* Full access to all uvc settings (Zoom,Focus,Brightness,etc.)
* Full access to all stream and format parameters (rates,sizes,etc.)
* Enumerate all capture devices with device_list()
* Capture instance will always grab mjpeg conpressed frames from cameras.

Image data is returned as `Frame` object. This object will decompress and convert on the fly when image data is requested.
This gives the user the full flexiblity: Grab just the jpeg buffers or have them converted to YUV or Gray or RGB and only when you need.

The `Frame` class has caching build in to avoid double decompression or conversion.

# Dependencies Linux

Follow the instructions on the (BRICS)[https://github.com/brown-ivl/brics] project to install python with Anaconda. Then install these:

```
conda install -c conda-forge cython pkgconfig
```

### libuvc
```
git clone https://github.com/pupil-labs/libuvc
cd libuvc
mkdir build
cd build
cmake ..
make && sudo make install
sudo ldconfig
```

### libjpeg-turbo
```
wget -O libjpeg-turbo.tar.gz https://sourceforge.net/projects/libjpeg-turbo/files/1.5.1/libjpeg-turbo-1.5.1.tar.gz/download
tar xvzf libjpeg-turbo.tar.gz
cd libjpeg-turbo-1.5.1
./configure --with-pic --prefix=/usr/local
sudo make install
sudo ldconfig
```

### OpenCV

We will use OpenCV 3.4+ with highgui and Python 3 support. First install some prerequisites:

On Ubuntu 20.04: `sudo apt install ffmpeg qt5-default libgtk2.0-dev libgtk-3-dev libpng-dev`
On Ubuntu 22.04: `sudo apt install ffmpeg libgtk2.0-dev libgtk-3-dev libpng-dev qtbase5-dev qtchooser qt5-qmake qtbase5-dev-tools`
On Odroid Ubuntu Mate 20.04: `sudo apt -o Dpkg::Options::="--force-overwrite" install ffmpeg`

Then get OpenCV:

```
wget https://github.com/opencv/opencv/archive/3.4.16.zip
```

Replace `ENV_PATH` and `PYTHON_VERSION` with the path of the python environment in your Anaconda (get it using `which python` when the environment is activated). For instance, first run

```
ENV_PATH=/home/srinath/anaconda3/envs/napier
PYTHON_VERSION=3.7m
```

Then do:

```
mkdir build

cd build

cmake \
-D CMAKE_BUILD_TYPE=RELEASE \
-D CMAKE_INSTALL_PREFIX=/usr/local \
-D INSTALL_PYTHON_EXAMPLES=ON \
-D OPENCV_GENERATE_PKGCONFIG=ON \
-D WITH_FFMPEG=ON \
-D WITH_QT=ON \
-D WITH_TIFF=OFF \
-D WITH_GTK=ON \
-D BUILD_opencv_python2=OFF \
-D BUILD_opencv_python3=ON \
-D PYTHON3_EXECUTABLE=$ENV_PATH/bin/python \
-D PYTHON3_INCLUDE_DIR=$ENV_PATH/include/python${PYTHON_VERSION} \
-D PYTHON3_LIBRARY=$ENV_PATH/lib/libpython${PYTHON_VERSION}.so \
-D PYTHON3_PACKAGES_PATH=$ENV_PATH/lib/python$PYTHON_VERSION/site-packages \
-D PYTHON3_NUMPY_INCLUDE_DIRS=$ENV_PATH/lib/python$PYTHON_VERSION/site-packages/numpy/core/include \
-D WITH_GSTREAMER=OFF \
..
```

After cmake completes successfully, run:

```
make -j 8
sudo make install
```

### udev rules for running as normal user:
```
echo 'SUBSYSTEM=="usb",  ENV{DEVTYPE}=="usb_device", GROUP="plugdev", MODE="0664"' | sudo tee /etc/udev/rules.d/10-libuvc.rules > /dev/null
sudo udevadm trigger
```

## Build Locally
```
python setup.py build_ext -i
```

## or install system wide
```
python setup.py install
```
