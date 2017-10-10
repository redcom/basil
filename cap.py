from CameraProperties import CameraProperties
from picamera import PiCamera
from picamera.array import PiRGBArray
import time
import os
import cv2
import math
import subprocess
from UtilityS3 import UploadFileToS3
from pyexif import ExifEditor
    
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (2592, 1952) # (2160, 1632) (2112, 1568) (2000, 1504) (1920, 1088) (1640, 1232)
camera.framerate = 5
rawCapture = PiRGBArray(camera, size=camera.resolution)
 
show = True

cp = CameraProperties(camera)
cp.Load()

last_picture_taken_ticks = -1  # todo: read this from disk
just_started = True
previous_digital_gain = -1.0
previous_analog_gain = -1.0

def UpdateGainDistance():
    global gain_distance
    global previous_analog_gain
    global previous_digital_gain
    gain_distance = math.fabs(camera.digital_gain - previous_digital_gain)
    gain_distance += math.fabs(camera.analog_gain - previous_analog_gain)
    previous_digital_gain = previous_digital_gain * .8 + .2 * camera.digital_gain
    previous_analog_gain = previous_analog_gain * .8 + .2 * camera.analog_gain
    print('analog %s  digital %s distance %s' % (float(camera.analog_gain),
                                                 float(camera.digital_gain),
                                                 gain_distance))

def PrintHelp():
    print('*' * 10)
    print('TAB - Print All Properties')
    print('Arrow Keys - Navigate Properties And Values')
    print('Enter - Set Current Property')
    print('F - Freeze')
    print('S - Save')
    print('D - Disable Display')
    print('H - Help')
    print('P - Take Picture Now')
    print('ESC - Exit')
    print('Z - Zoom To Focus')
    print('*' * 10)

def TakePicture(img, res):
    print('Saving picture.')
    note = os.environ['BASIL_NOTE']
    filename = 'cache/' + note + '_' + str(res[0]) + 'x' + str(res[1]) + '_' + time.strftime("%Y_%m_%d-%H_%M.jpg")
    print(filename)
    cv2.imwrite(filename, img)
    global last_picture_taken_ticks
    last_picture_taken_ticks = time.time()  # todo: write this to disk
    # add EXIF keywords
    exif = ExifEditor(filename)
    # exif.addKeyword('tre')
    exif.addKeywords([git_commit_message, time_process_started_string])
    print('getKeywords', exif.getKeywords())
    print('getTag Keywords', exif.getTag("Keywords"))

# allow the camera to warmup
print('Wait...')
time.sleep(1)

# git_hash = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip()
# print(git_hash)
git_commit_message = subprocess.check_output(["git", "log", "-1"]).strip()  # , "--pretty=%B"
print(git_commit_message)

time_process_started = time.time()
time_process_started_string = time.strftime("started %Y/%m/%d %H:%M")

cv2.namedWindow('cap', cv2.WINDOW_NORMAL)
      
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=False):
	# grab the raw NumPy array representing the image
	image = frame.array  # todo: maybe we can avoid this if not just started and not showing and not taking the picture
 
	# show the frame
	if show:
            cv2.imshow('cap', image)

        if just_started:
            UpdateGainDistance()
            if gain_distance < 0.05:
                just_started = False
                cp.SetAllPropertiesOnCamera()
                # todo: do the rest after one second or so...
                PrintHelp()
                cp.PrintCurrentProperty()
                show = False
                print('Display disabled.')
        else:
          ticks = time.time()
          if (ticks - last_picture_taken_ticks) > 61.0:
              localtime = time.localtime(ticks) # gmtime for UTC
              if localtime.tm_min == 19:  # one per hour
                  # if localtime.tm_hour == 10:  # one per day
                  TakePicture(image, camera.resolution)
        
        key = cv2.waitKey(50) & 0xFF  # milliseconds
        
        if (key < 255 and key != ord('d')):
            # print(key)
            if show == False:
              print('Display enabled.')
              show = True
        
        if key == ord('d'):
            print('Display disabled.')
            show = False
        
        if key == ord('h'):
            PrintHelp()
        
        if key == ord('s'):
            cp.Save()
        
        if key == ord('f'):
            cp.FreezeExposureAWB()

        if key == ord('p'):
            TakePicture(image, camera.resolution)

        if key == 10:  # enter
            cp.SetPropertyOnCamera(cp.CurrentPropertyName(),
                                   cp.CurrentPropertyValue())
    
        if key == 9:  # tab
            cp.PrintAllProperties()
            # print(git_hash)
            print(git_commit_message)
            uptime_minutes = int((time.time() - time_process_started) / (60.0))
            print(time_process_started_string) 
            print(time.strftime("now %Y/%m/%d %H:%M"))
            print('uptime minutes %s' % uptime_minutes)
            print('*' * 20)

            
        if key == ord('z'):    
            if camera.zoom[0] == 0.0:
                camera.zoom = (0.333, 0.333, 0.333, 0.333)
            else:
                camera.zoom = (0.0, 0.0, 1.0, 1.0)
                   
        if key == 82:  # up
            cp.DecProperty()
        
        if key == 84: # down
            cp.IncProperty()
            
        if key == 81: # left
            cp.DecValue()
            
        if key == 83:  # right
            cp.IncValue()
 
	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)
 
	# if the `q` or ESC key was pressed, break from the loop
	if key == ord('q') or key == 27:
		break
		
camera.close()
print('Camera closed.')
cv2.destroyAllWindows()
print('Windows destroyed.')

# UploadFileToS3('somefile.txt')
