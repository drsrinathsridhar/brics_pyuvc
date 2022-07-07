Install Ubuntu 20.04.

## Install Anaconda and setup environment

Setup an environment using anaconda and activate it.

`conda create -n napier python=3.6`

## Build OpenCV

First build OpenCV 3.4+ with highgui and Python 3 support. First install some prerequisites:

`sudo apt install ffmpeg qt5-default libgtk2.0-dev libgtk-3-dev`

Here's the CMAKE command. Please replace `ENV_PATH` with the path of the python environment in your Anaconda (get it using `which python` when the environment is activated).

For instance, first run

`ENV_PATH=/home/srinath/anaconda3/envs/napier`

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
-D PYTHON3_LIBRARY=$ENV_PATH/lib/libpython3.6m.so \
-D PYTHON3_INCLUDE_DIR=$ENV_PATH/include/python3.6m \
-D PYTHON3_EXECUTABLE=$ENV_PATH/bin/python \
-D PYTHON3_PACKAGES_PATH=$ENV_PATH/lib/python3.6/site-packages \
-D PYTHON3_NUMPY_INCLUDE_DIRS=$ENV_PATH/lib/python3.6/site-packages/numpy/core/include \
-D WITH_GSTREAMER=OFF \
..
```

After cmake completes succuessfully, run:

```
make -j 8
sudo make install
```

## Follow pyuvc instructions

README.md
