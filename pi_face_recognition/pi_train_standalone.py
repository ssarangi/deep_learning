from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import sys
import time

camera = PiCamera()
size = (640, 480)
camera.resolution = size
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=size)

# Allow the camera to warm up
time.sleep(0.1)

cascPath = sys.argv[1]


for camera_frame in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
    frame = camera_frame.array

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # Display the resulting frame
    cv2.imshow('Video', frame)

    rawCapture.truncate(0)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
cv2.destroyAllWindows()