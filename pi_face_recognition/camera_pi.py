import time
import io
import threading
import picamera
from picamera.array import PiRGBArray
import cv2

class Camera(object):
    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera
    faceCascade = None
    current_frame = 0

    def initialize(self):
        if Camera.thread is None:
            # start background frame thread
            Camera.faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.start()

            # wait until frames start to be available
            while self.frame is None:
                time.sleep(0)
                

    def get_frame(self):
        Camera.last_access = time.time()
        self.initialize()
        return self.frame

    @classmethod
    def _thread(cls):
        with picamera.PiCamera() as camera:
            # camera setup
            size = (320, 240)
            camera.resolution = size
            camera.framerate = 32
            camera.hflip = True
            camera.vflip = True

            # let camera warm up
            time.sleep(2)

            stream = PiRGBArray(camera, size=(320, 240))
            for foo in camera.capture_continuous(stream, 'bgr',
                                                 use_video_port=True):
                
                frame = foo.array
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
                faces = cls.faceCascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30),
                    flags=cv2.CASCADE_SCALE_IMAGE
                )
            
                # Draw a rectangle around the faces
                for idx, (x, y, w, h) in enumerate(faces):
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cropped = frame[y:y+h, x:x+w]
                    cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
                    cv2.imwrite('data/saty/%s_%s.png' % (cls.current_frame, idx), cropped)
                    
                                
                # store frame
                imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
 
                cls.current_frame += 1
                
                success, cls.frame = cv2.imencode('.jpg', imgRGB)
                cls.frame = cls.frame.tobytes()

                # reset stream for next frame
                stream.seek(0)
                stream.truncate()

                # if there hasn't been any clients asking for frames in
                # the last 10 seconds stop the thread
                if time.time() - cls.last_access > 10:
                    break
        cls.thread = None
