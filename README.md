# Security Webcams (With python)

*The project is currently in devlopping state*

current version: 0.1.1 

## What it does

It use all the available webcams and can detect if a person is facing the webcam and trigger a sound alarm

It can save the frames where a face is detected and it can also save all the frames if you wish (see the init.ini file)

## Requierements

Coded with Python 3.11

Python libraries:

* fnmatch
* time
* datetime
* os
* multiprocessing
* cv2
* playsound
* sys

Hardware:

* USB webcams
* A good enough computer
* free space to store the frames

OS:

I only tested it on linux fedora.

## How to use it

Run the python file in your terminal and it should do the trick

## What should be in the next updates

* Better exception handling
* Auto deleting frames after a certain amount of time
* The possibility to have a different configuration for each webcam
* A cleaner code
* The possibility of reframing the webcams
* Asynchronous frame display - frame saving
* Optimization (maybe switching to Cython?)


## Init.ini


face_detection

* True = toggle the face detection
* False = don't toggle the face detection

Display

* True = display what webcams are seeing on your display
* False = don't show what webcams are seeing

wait_interval 

* time between two frames in seconds

Save_all_frames

* True = saving all the frames
* False = not saving the frames

Save_frame_with_face

*The face_detection must be active*

* True = Save the frames where at least a face is detected
* False = not saving the frames where at least a face is detected

location

* Where to store the frames

location_face

* Where to store the frames with faces in them

waiting_between_checks

* Time between check if a face was detected since last time to ring the alarm

location_sound

* location of your alarm sound file
