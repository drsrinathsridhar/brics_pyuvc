Install Ubuntu 20.04.

1. Install Anaconda

2. Setup an environment using anaconda and activate it.

`conda create -n napier python=3.6`

3. First build OpenCV 3.4+ with highgui and Python 3 support. Here's the CMAKE command. Please replace `ENV_PATH` with the path of the python environment in your Anaconda (get it using `which python` when the environment is activated).

For instance, first runnnnnnnn

`ENV_PATH=/home/srinath/anaconda3/envs/napier`

Then do

`cmake \
-D CMAKE_BUILD_TYPE=RELEASE \
-D CMAKE_INSTALL_PREFIX=/usr/local \
-D INSTALL_PYTHON_EXAMPLES=ON \
-D OPENCV_GENERATE_PKGCONFIG=ON \
-D WITH_FFMPEG=ON \
-D WITH_QT=ON \
-D WITH_TIFF=OFF \
-D WITH_GTK=ON \
-D BUILD_opencv_python2=OFF \
-D BUILD_opencv_python3=OFF \
-D PYTHON3_LIBRARY=$ENV_PATH/lib/libpython3.6m.so \
-D PYTHON3_INCLUDE
