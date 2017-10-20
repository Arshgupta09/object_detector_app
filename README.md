# Object-Detector-App

A real-time object recognition application using [Google's TensorFlow Object Detection API](https://github.com/tensorflow/models/tree/master/object_detection) and [OpenCV](http://opencv.org/).

## Getting Started

1. Copy the files
```
git clone https://github.com/h3dema/object_detector_app.git
cd object_detector_app
git submodule init
git submodule update
```

2. Prepare the environment to run the application
```
conda env create -f environment.yml
sudo apt-get install protobuf-compiler python-pil python-lxml
```

3. `source activate object-detection`

4. `python object_detection_app.py`
    Optional arguments (default value):
    * Device index of the camera `--source=0`
    * Width of the frames in the video stream `--width=480`
    * Height of the frames in the video stream `--height=360`
    * Number of workers `--num-workers=2`
    * Size of the queue `--queue-size=5`

Please note that our app uses Python version 3.

## Quitting the program

Just click on the video screen and type the key 'q'.

## Second access

If you want to use the program again, you don't have to use the commands 1 and 2 again
Just cd to the directory
```
cd object_detector_app
source activate object-detection
python object_detection_app.py
```

## Leave anaconda environment ##

To leave the anaconda environment, just type the command:
```
source deactivate
```

## Requirements

* Python 2.7
* git
* protobuf-compiler
* You need to install Anaconda to run the programs shown here. Go to [conda installation](https://conda.io/docs/user-guide/install/index.html) do see how to install. Go to [downloads](https://www.anaconda.com/download/) to download Anaconda.
```
wget -c https://repo.continuum.io/archive/Anaconda2-5.0.0-Linux-x86_64.sh
bash Anaconda2-5.0.0-Linux-x86_64.sh
```
* File [environment.yml](https://github.com/h3dema/object_detector_app/blob/master/environment.yml) lists all requirements to build the Anaconda environment.

## Uninstall ##

```
conda env remove object-detection
rm -fr ~/anaconda3/envs/object-detection
```

## Training Data ##

Data used in this example can be found in https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md. We are using **ssd_mobilenet_v1_coco**.

## Notes
- This program was tested using Ubuntu 14 with OpenCV 3.3.
- OpenCV 3.1 might crash on OSX after a while, so that's why I had to switch to version 3.0. See open issue and solution [here](https://github.com/opencv/opencv/issues/5874).
- Moving the `.read()` part of the video stream in a multiple child processes did not work. However, it was possible to move it to a separate thread.

## Thanks

This repository comes from a fork from [Dat Tran](http://www.dat-tran.com/).
