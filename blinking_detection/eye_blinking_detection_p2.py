from __future__ import print_function
import cv2
import numpy as np
import dlib
from math import hypot
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread

# import the necessary packages
from imutils.video.pivideostream import PiVideoStream
from imutils.video import FPS
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import imutils
import time
import requests
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

def send_face(frame1, frame2, amount):
    # TODO: Send Frames to Flask 
    print("Blink sent to Flask")
    cv2.imwrite("image1.jpg", frame1)
    cv2.imwrite("image2.jpg", frame2)
    multipart_form_data = {
        'file1': ("image1.jpg", open("image1.jpg", 'rb')),
        'file2': ("image2.jpg", open("image2.jpg", 'rb')),
        'amount': amount,
        'pos': 12345
    }
    requests.post('http://192.168.10.140:5001/', data={"amount": amount, "pos": 12345}, files={"file1": open("image1.jpg", 'rb'), "file2": open("image2.jpg", 'rb')})



def midpoint(p1 ,p2):
    return int((p1.x + p2.x)/2), int((p1.y + p2.y)/2)

font = cv2.FONT_HERSHEY_PLAIN

def get_blinking_ratio(eye_points, facial_landmarks):
    left_point = (facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y)
    right_point = (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y)
    center_top = midpoint(facial_landmarks.part(eye_points[1]), facial_landmarks.part(eye_points[2]))
    center_bottom = midpoint(facial_landmarks.part(eye_points[5]), facial_landmarks.part(eye_points[4]))

    hor_line_lenght = hypot((left_point[0] - right_point[0]), (left_point[1] - right_point[1]))
    ver_line_lenght = hypot((center_top[0] - center_bottom[0]), (center_top[1] - center_bottom[1]))

    ratio = hor_line_lenght / ver_line_lenght
    return ratio

continuousFrames = 0



# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-n", "--num-frames", type=int, default=100,
	help="# of frames to loop over for FPS test")
ap.add_argument("-d", "--display", type=int, default=-1,
	help="Whether or not frames should be displayed")
args = vars(ap.parse_args())

# initialize the camera and stream
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=(640, 480))
stream = camera.capture_continuous(rawCapture, format="bgr",
	use_video_port=True)

# allow the camera to warmup and start the FPS counter
print("[INFO] sampling frames from `picamera` module...")
time.sleep(2.0)
fps = FPS().start()

# loop over some frames
frameback = {}
amount = input()
for (i, f) in enumerate(stream):
	# grab the frame from the stream and resize it to have a maximum
	# width of 400 pixels
	frame = f.array
	frame = imutils.resize(frame, width=400)

	# check to see if the frame should be displayed to our screen
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = detector(gray)
        if len(faces)==1:
            face = faces[0]
        #x, y = face.left(), face.top()
        #x1, y1 = face.right(), face.bottom()
        #cv2.rectangle(frame, (x, y), (x1, y1), (0, 255, 0), 2)

            landmarks = predictor(gray, face)

            left_eye_ratio = get_blinking_ratio([36, 37, 38, 39, 40, 41], landmarks)
            right_eye_ratio = get_blinking_ratio([42, 43, 44, 45, 46, 47], landmarks)
            blinking_ratio = (left_eye_ratio + right_eye_ratio) / 2

            if blinking_ratio > 4:
                continuousFrames+=1
            else:
                if continuousFrames>=5:
                    send_face(frame, frameback, amount)
                    amount = input()
                continuousFrames = 0
                frameback=frame
        else:
            continuousFrames=0
        print(continuousFrames)


        cv2.imshow("Frame", frame)

        key = cv2.waitKey(1)
        if key == 27:
            break


	# clear the stream in preparation for the next frame and update
	# the FPS counter
	rawCapture.truncate(0)
	fps.update()


# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
stream.close()
rawCapture.close()
camera.close()
