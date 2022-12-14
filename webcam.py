#things to do 
#1. clean the code
#2. add try and except
#3. add the possibility to have different configuration for each webcam


import fnmatch
import time
import datetime
import os
import multiprocessing
import cv2
import playsound
import sys

#General purpose class 
######################################################################################################################################
###################################################################################################################### CLASS directory
######################################################################### S  METHOD __init__                          self,str -> None
######################################################################### _  METHOD create_directory                  self     -> None
######################################################################### s  METHOD have_the_number_of_files_changed  self     -> bool
######################################################################### _  METHOD get_number_of_files               self     -> int
######################################################################### S  METHOD update_the_number_of_files        self     -> None

class directory:

    """Folder class that can create a folder and gives information about it's state"""
    # This class creates a directory and gives information about it's state

    def __init__(self, location : str) -> None :

        self.location = location
        self.create_directory()
        self.number_of_files = len(fnmatch.filter(os.listdir(location), '*.*'))

        return None
    
    def create_directory(self) -> None :

        """Creates a directory"""

        if not os.path.exists(self.location):
            os.makedirs(self.location)

        return None

    def have_the_number_of_files_changed(self) -> bool :

        """Checks if the number of files in the directory has changed"""

        if self.number_of_files != len(fnmatch.filter(os.listdir(self.location), '*.*')):
            self.number_of_files = len(fnmatch.filter(os.listdir(self.location), '*.*'))
            return True

        else:

            return False

    def get_number_of_files(self) -> int :
                
        """Returns the number of files in the directory"""
    
        return self.number_of_files

    def update_the_number_of_files(self) -> None :
                
        """Updates the number of files in the directory"""
    
        self.number_of_files = len(fnmatch.filter(os.listdir(self.location), '*.*'))

        return None

######################################################################################################################################
######################################################################################################################################



#General purpose functions 
######################################################################################################################################
############################################################################################### PROCEDURE save_frame_as_jpeg_in_folder

def save_frame_as_jpeg_in_folder(frame : any, location : str, camera_id : int) -> None :

    """Saves a frame as a jpeg image in a folder"""
    # This function saves a frame as a jpeg image in a folder

    if not os.path.exists(location):
        os.makedirs(location)

    now = datetime.datetime.now()
    name = now.strftime("%Y-%m-%d-%H-%M-%S-%f") +"-CAM-"+ str(camera_id//2)
    cv2.imwrite(location + "/" + name + ".jpg", frame)

    return None

########################################################################################################## T FUNCTION cameras_detector

def cameras_detector() -> list[int] :

    """Detects the number of cameras connected to the computer and their ids"""
    # This is a generator that yields the number of cameras connected to the computer and returns their ids

    devices = os.listdir("/dev")
    cameras_indices = [int(device[-1]) for device in devices 
                      if (device.startswith("video") and not(int(device[-1]) % 2))]
    cameras_indices.sort()

    return cameras_indices

################################################################################################################# PROCEDURE play_sound

def play_sound(sound_file : str) -> None :

    """Plays a sound file"""
    # This function plays a sound file

    playsound.playsound(sound_file)

    return None

################################################################################################### T FUNCTION face_detection_in_frame

def face_detection_in_frame(frame : any) -> any:

    """Detects faces in a frame"""
    # This function detects faces in a frame

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    return faces

###################################################################################################### T Function ini_reader(location)

def ini_reader(location : str) -> dict():

    """Reads an ini file and returns a dictionary with the values"""
    # This function reads an ini file and returns a dictionary with the values

    with open(location, "r") as file:
        lines = file.readlines()

    lines = [line.strip() for line in lines if not(line.startswith("#"))]
    lines = [line.split("=") for line in lines if not(line == "")]
    lines = [(line[0].strip(), line[1].strip()) for line in lines]

    return dict(lines)


######################################################################################################################################
######################################################################################################################################



#specific functions 
######################################################################################################################################
############################################################################################################## PROCEDURE global_camera

def global_camera(id : int, 
                  face_detection = True, 
                  Display = True, 
                  wait_interval = 0.25, 
                  Save_all_frames = False,
                  Save_frame_with_face = True,
                  location_frames = "frames",
                  location_face = "faces_detected") -> None:

    """Detects faces in a camera and displays the camera and store the current frame in a folder as a jpeg if a face is detected"""
    # This function detects faces in a camera and displays the camera and store the frame in a folder as a jpeg if a face is detected

    camera = cv2.VideoCapture(id)

    while True:

        _, frame = camera.read()

        if face_detection:

            faces = face_detection_in_frame(frame)

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

                if Save_frame_with_face:
                    save_frame_as_jpeg_in_folder(frame, location_face, id)
        
                
        if Save_all_frames:
            save_frame_as_jpeg_in_folder(frame, location_frames, id)

        if Display:
            cv2.imshow("Camera: " + str(id//2), frame)

        if cv2.waitKey(1) == 27:
            print("Camera: " + str(id//2) + " killed by user")
            break

        time.sleep(wait_interval)

    cv2.destroyAllWindows()

    return None

######################################################################################################## PROCEDURE global_alarm_ringer

def global_alarm_ringer(sound_location : str, ring_time = 30) -> None :

        """Plays a sound file for a given time"""
        # This function plays a sound file for a given time
    
        start = time.time()

        while time.time() - start < ring_time:
            play_sound(sound_location)
    
        return None

############################################################################################################### PROCEDURE global_alarm

def global_alarm(location : str, sound_location : str, ring_time = 30, waiting_between_checks = 10) -> None:

        """Detects if directory change in number of file and if it is the case make alarm ring"""
        # This function detects if directory change in number of file and if it is the case make alarm ring

        folder = directory(location)

        while True:

            if folder.have_the_number_of_files_changed():
                global_alarm_ringer(sound_location, ring_time)

            time.sleep(waiting_between_checks)

        return None

######################################################################################################################################
######################################################################################################################################



#main function & global_launcher function
######################################################################################################################################
################################################################################################################################# MAIN

def main() -> None:
    
        """Runs the security system"""
        # This function runs the security system

        arguments = ini_reader("config/init.ini")

        cameras_indices = cameras_detector()

        if "face_detection" in arguments.keys():

            face_detection = arguments["face_detection"]

            if face_detection == "True":

                face_detection = True

            else:

                face_detection = False

        else:

            face_detection = True


        if "Display" in arguments.keys():

            Display = arguments["Display"]

            if Display == "True":

                Display = True

            else:

                Display = False

        else:

            Display = True


        if "wait_interval" in arguments.keys():

            wait_interval = float(arguments["wait_interval"])

        else:

            wait_interval = 0.25


        if "Save_all_frames" in arguments.keys():

            Save_all_frames = arguments["Save_all_frames"]

            if Save_all_frames == "True":

                Save_all_frames = True

            else:

                Save_all_frames = False 

        else:

            Save_all_frames = False

        
        if "Save_frame_with_face" in arguments.keys():

            Save_frame_with_face = arguments["Save_frame_with_face"]

            if Save_frame_with_face == "True":

                Save_frame_with_face = True
            
            else:

                Save_frame_with_face = False

        else:

            Save_frame_with_face = True

        
        if "Alarm" in arguments.keys():

            Alarm = arguments["Alarm"]

            if Alarm == "True":
                    
                    Alarm = True
            
            else:
                    
                    Alarm = False

        else:

            Alarm = True


        if "location_frames" in arguments.keys():

            location_frames = arguments["location_frames"]

        else:

            location_frames = "frames"


        if "location_face" in arguments.keys():

            location_face = arguments["location_face"]

        else:

            location_face = "faces_detected"


        if "location_sound" in arguments.keys():

            location_sound = arguments["location_sound"]

        else:

            location_sound = "sounds/alarm.mp3"

        
        if "ring_time" in arguments.keys():

            ring_time = float(arguments["ring_time"])

        else:

            ring_time = 30

        
        if "waiting_between_checks" in arguments.keys():

            waiting_between_checks = float(arguments["waiting_between_checks"])

        else:

            waiting_between_checks = 10


        global_security_system(cameras_indices,
                               face_detection,
                               Display,
                               wait_interval,
                               Save_all_frames,
                               Save_frame_with_face,
                               Alarm,
                               location_frames,
                               location_face,
                               location_sound,
                               ring_time,
                               waiting_between_checks)
    
        return None

######################################################################################################################################
############################################################################################################### GLOBAL_SECURITY_SYSTEM


def global_security_system(cameras_indices = cameras_detector(), 
                           face_detection = True, 
                           Display = True, 
                           wait_interval = 0.25, 
                           Save_all_frames = False,
                           Save_frame_with_face = True,
                           Alarm = True,
                           location_frames = "frames",
                           location_face = "faces_detected",
                           location_sound = "sounds/alarm.mp3",
                           ring_time = 30,
                           waiting_between_checks = 10) -> None:

    """Runs the security system"""
    # This function runs the security system


    processes = [multiprocessing.Process(target=global_camera, 
                                         args=(id, 
                                               face_detection, 
                                               Display, 
                                               wait_interval, 
                                               Save_all_frames, 
                                               Save_frame_with_face, 
                                               location_frames, 
                                               location_face)) 
                                                                    for id in cameras_indices]

    if Alarm:
        processes.append(multiprocessing.Process(target=global_alarm,
                                                  args=(location_frames,
                                                        location_sound,
                                                        ring_time,
                                                        waiting_between_checks)))


    for process in processes:
        process.start()

    for process in processes:
        process.join()

    return None


######################################################################################################################################
######################################################################################################################################



#OLD function that are not used nor maintained anymore
########################################################################## PROCEDURE display_camera

def display_camera(id : int) -> None:

    """Displays the camera"""
    # This function displays the camera

    camera = cv2.VideoCapture(id)

    while True:

        _, frame = camera.read()
        cv2.imshow("Camera: " + str(id//2), frame)

        if cv2.waitKey(1) == 27:
            break

    cv2.destroyAllWindows()
    
    return None

######################################################################### PROCEDURE display_cameras

def display_cameras(cameras_indices = cameras_detector()) -> None :

    """Displays a series of cameras by their ids"""
    # This function displays a series of cameras by their ids

    cameras = [multiprocessing.Process(target=display_camera, args=(id,)) for id in cameras_indices]

    for camera in cameras:
        camera.start()

    for camera in cameras:
        camera.join()

    return None

###################################################### PROCEDURE display_camera_with_face_detection

def display_camera_with_face_detection(id : int) -> None :

    """Displays the camera and detects faces"""
    # This function displays the camera and detects faces

    camera = cv2.VideoCapture(id)

    while True:

        _, frame = camera.read()
        faces = face_detection_in_frame(frame)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        cv2.imshow("Camera: " + str(id//2), frame)

        if cv2.waitKey(1) == 27:
            break

    cv2.destroyAllWindows()

    return None

##################################################### PROCEDURE display_cameras_with_face_detection

def display_cameras_with_face_detection(cameras_indices = cameras_detector()):

    """Displays a series of cameras by their ids and detects faces"""
    # This function displays a series of cameras by their ids and detects faces

    cameras = [multiprocessing.Process(target=display_camera_with_face_detection, args=(id,)) for id in cameras_indices]

    for camera in cameras:
        camera.start()

    for camera in cameras:
        camera.join()

    return None

############################################################ PROCEDURE save_frame_as_jpeg_in_folder

def security_camera_face_detection(id,wait_interval = 0, location = "faces_detected") -> None:

    """Detects faces in a camera"""
    # This function detects faces in a camera and store the current frame in a folder as a jpeg if a face is detected

    camera = cv2.VideoCapture(id)

    while True:

        _, frame = camera.read()
        faces = face_detection_in_frame(frame)

        if len(faces) > 0:
            save_frame_as_jpeg_in_folder(frame, location, id)

        if cv2.waitKey(1) == 27:
            break

        time.sleep(wait_interval)

    cv2.destroyAllWindows()

    return None

########################################################### PROCEDURE save_frames_as_jpeg_in_folder

def security_cameras_face_detection(cameras_indices = cameras_detector(), wait_interval = 0, location = "faces_detected") -> None:

    """Detects faces in a series of cameras by their ids"""
    # This function detects faces in a series of cameras by their ids and store the frame in a folder as a jpeg if a face is detected

    cameras = [multiprocessing.Process(target=security_camera_face_detection, args=(id,wait_interval)) for id in cameras_indices]

    for camera in cameras:
        camera.start()

    for camera in cameras:
        camera.join()

    return None

############################################## PROCEDURE security_camera_face_detection_and_display

def security_camera_face_detection_and_display(id,wait_interval = 0, location = "faces_detected"):

    """Detects faces in a camera and displays the camera and store the current frame in a folder as a jpeg if a face is detected"""
    # This function detects faces in a camera and displays the camera and store the current frame in a folder as a jpeg if a face is detected

    camera = cv2.VideoCapture(id)

    while True:

        _, frame = camera.read()
        faces = face_detection_in_frame(frame)

        if len(faces) > 0:
            save_frame_as_jpeg_in_folder(frame, location, id)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        cv2.imshow("Camera: " + str(id//2), frame)

        if cv2.waitKey(1) == 27:
            break

        time.sleep(wait_interval)

    cv2.destroyAllWindows()

    return None

############################################# PROCEDURE security_cameras_face_detection_and_display

def security_cameras_face_detection_and_display(cameras_indices = cameras_detector(), wait_interval = 0, location = "faces_detected") -> None :

    """Detects faces in a series of cameras by their ids and displays the cameras and store the frame in a folder as a jpeg if a face is detected"""
    # This function detects faces in a series of cameras by their ids and displays the cameras and store the frame in a folder as a jpeg if a face is detected

    cameras = [multiprocessing.Process(target=security_camera_face_detection_and_display, args=(id,wait_interval,location)) for id in cameras_indices]

    for camera in cameras:
        camera.start()

    for camera in cameras:
        camera.join()

    return None

##################################################################### PROCEDURE security_ring_alarm

def security_ring_alarm(file_location : str) -> None :

    """Plays a sound file"""
    # This function plays a sound file

    playsound.playsound(file_location)

    return None

########################################################################## PROCEDURE global_cameras

def global_cameras(cameras_indices = cameras_detector(), 
                  face_detection = True, 
                  Display = True, 
                  wait_interval = 0.25, 
                  Save_all_frames = False,
                  Save_frame_with_face = True,
                  location = "frames",
                  location_face = "faces_detected") -> None :

    """Detects faces in a series of cameras and displays the cameras and store the current frame in a folder as a jpeg"""
    # This function detects faces in a series of cameras and displays the cameras and store the frame in a folder as a jpeg

    cameras = [multiprocessing.Process(target=global_camera, 
                                       args=(id, 
                                             face_detection, 
                                             Display, 
                                             wait_interval, 
                                             Save_all_frames, 
                                             Save_frame_with_face, 
                                             location, 
                                             location_face)) 
               for id in cameras_indices]

    for camera in cameras:
        camera.start()

    for camera in cameras:
        camera.join()

    return None

###################################################################################################




###################################################################################################################################### START OF
###################################################################################################################################### PROGRAM


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Program interrupted by user")
        sys.exit(0)


###################################################################################################################################### END OF
###################################################################################################################################### PROGRAM