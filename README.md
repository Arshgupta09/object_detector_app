# Object-Detector-App

A real-time object recognition application using [Google's TensorFlow Object Detection API](https://github.com/tensorflow/models/tree/master/object_detection) and [OpenCV](http://opencv.org/).

## Getting Started
1. `conda env create -f environment.yml`
2. `python object_detection_app.py` 
    Optional arguments (default value):
    * Device index of the camera `--source=0`
    * Width of the frames in the video stream `--width=480`
    * Height of the frames in the video stream `--height=360`
    * Number of workers `--num-workers=2`
    * Size of the queue `--queue-size=5`

## Quitting the program

Just click on the video screen and type the key 'q'.

## Second access

If you want to use the program again, you don't have to use the firts commando conda env ....
Just cd to the directory
```
cd object_detector_app
source activate object-detection
python object_detection_app.py
```

## Leave anaconda environment ##

To leave the anaconda environment, just type the command:
```
source deactivate object-detection
```

## Tests
```
pytest -vs utils/
```

## Requirements

* Python 2.7
* Git
* You need to install Anaconda to run the programs shown here.
* File [environment.yml](https://github.com/h3dema/object_detector_app/blob/master/environment.yml) lists all requirements to build the Anaconda environment.

## object_detection ##

The directory object_detection comes from https://github.com/tensorflow/models/tree/master/research/object_detection.

## Notes
- This program was tested using Ubuntu 14 with OpenCV 3.3.
- OpenCV 3.1 might crash on OSX after a while, so that's why I had to switch to version 3.0. See open issue and solution [here](https://github.com/opencv/opencv/issues/5874).
- Moving the `.read()` part of the video stream in a multiple child processes did not work. However, it was possible to move it to a separate thread.

## Thanks

This repository comes from a fork from [Dat Tran](http://www.dat-tran.com/).
