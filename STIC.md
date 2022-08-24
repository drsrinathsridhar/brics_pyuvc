Install Ubuntu 20.04.

## Install Anaconda and setup environment

Setup an environment using anaconda and activate it.

`conda create -n napier python=3.7`

## Build OpenCV

Get OpenCV:

`wget https://github.com/opencv/opencv/archive/3.4.16.zip`

First build OpenCV 3.4+ with highgui and Python 3 support. First install some prerequisites:

`sudo apt install ffmpeg qt5-default libgtk2.0-dev libgtk-3-dev libpng-dev`

(On Ubuntu 22.04 try `sudo apt-get install qtbase5-dev qtchooser qt5-qmake qtbase5-dev-tools` instead of `qt5-default`).
(On Odroid Ubuntu Mate 20.04, try `sudo apt -o Dpkg::Options::="--force-overwrite" install ffmpeg`

Here's the CMAKE command. Please replace `ENV_PATH` with the path of the python environment in your Anaconda (get it using `which python` when the environment is activated).

For instance, first run

`ENV_PATH=/home/srinath/anaconda3/envs/napier`
`PYTHON_VERSION=3.7m`

Then do

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

## Follow pyuvc instructions

README.md
