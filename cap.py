from CameraProperties import CameraProperties
from picamera import PiCamera
from picamera.array import PiRGBArray
import time
import cv2
import math
    
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (1280, 1024)
camera.framerate = 3
rawCapture = PiRGBArray(camera, size=camera.resolution)
 
# allow the camera to warmup
time.sleep(2)

show = True

cp = CameraProperties (camera)
cp.Load()

just_started = True
previous_digital_gain = -1.0
previous_analog_gain = -1.0

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
	image = frame.array
 
	# show the frame
	if show:
            cv2.imshow("Frame", image)
        # show = False
        key = cv2.waitKey(1) & 0xFF
        
        if just_started:
            gain_distance = math.fabs(camera.digital_gain - previous_digital_gain)
            gain_distance += math.fabs(camera.analog_gain - previous_analog_gain)
            previous_digital_gain = previous_digital_gain * .8 + .2 * camera.digital_gain
            previous_analog_gain = previous_analog_gain * .8 + .2 * camera.analog_gain
            print('analog %s  digital %s distance %s' % (float(camera.analog_gain), float(camera.digital_gain), gain_distance))
            if gain_distance < 0.05:
                just_started = False
                cp.SetAllPropertiesOnCamera()
                cp.PrintCurrentProperty()
                    
        if key < 255:
            pass
            # just_started = False
            # print (key)
        
        if key == ord('s'):
            cp.Save()
        
        if key == ord('f'):
            cp.FreezeExposureAWB()

        if key == 10:  # enter
            cp.SetPropertyOnCamera(cp.CurrentPropertyName(), cp.CurrentPropertyValue())
          
        if key == ord('c'):
            cp.PrintCurrentProperty()
    
        if key == 225: # left shift
            just_started = False
            cp.SetAllPropertiesOnCamera()
            cp.PrintAllProperties()
            cp.PrintCurrentProperty()
    
        if key == 9:  # tab
            cp.PrintAllProperties()
          
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
