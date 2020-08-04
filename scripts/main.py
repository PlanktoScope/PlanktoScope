################################################################################
#Actuator Libraries
################################################################################

#Library for exchaning messages with Node-RED
import paho.mqtt.client as mqtt

#Library to control the PiCamera
import picamera

#Libraries to control the steppers for focusing and pumping
from adafruit_motor import stepper
from adafruit_motorkit import MotorKit

#Import the planktonscope LED module
import planktonscope.light

################################################################################
#Practical Libraries
################################################################################

#Library to get date and time for folder name and filename
from datetime import datetime, timedelta

#Library to be able to sleep for a duration
from time import sleep

#Libraries manipulate json format, execute bash commands
import json, shutil, os, subprocess

################################################################################
#Morphocut Libraries
################################################################################

from skimage.util import img_as_ubyte
from morphocut import Call
from morphocut.contrib.ecotaxa import EcotaxaWriter
from morphocut.contrib.zooprocess import CalculateZooProcessFeatures
from morphocut.core import Pipeline
from morphocut.file import Find
from morphocut.image import (ExtractROI,
    FindRegions,
    ImageReader,
    ImageWriter,
    RescaleIntensity,
    RGB2Gray
)
from morphocut.stat import RunningMedian
from morphocut.str import Format
from morphocut.stream import TQDM, Enumerate, FilterVariables

################################################################################
#Other image processing Libraries
################################################################################

from skimage.feature import canny
from skimage.color import rgb2gray, label2rgb
from skimage.morphology import disk
from skimage.morphology import erosion, dilation, closing
from skimage.measure import label, regionprops
import cv2

################################################################################
#Streaming PiCamera over server
################################################################################
import io
import logging
import socketserver
from threading import Condition
from http import server
import threading

################################################################################
#Creation of the webpage containing the PiCamera Streaming
################################################################################

PAGE="""\
<html>
<head>
<title>PlanktonScope v2 | PiCamera Streaming</title>
</head>
<body>
<img src="stream.mjpg" width="640" height="480" />
</body>
</html>
"""

################################################################################
#Classes for the PiCamera Streaming
################################################################################

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

################################################################################
#MQTT core functions
################################################################################

#Run this function in order to connect to the client (Node-RED)
def on_connect(client, userdata, flags, rc):
    #Print when connected
    print("Connected! - " + str(rc))
    #When connected, run subscribe()
    client.subscribe("actuator/#")
    #Turn green the light module
    planktonscope.light.setRGB(0,255,0)

#Run this function in order to subscribe to all the topics begining by actuator
def on_subscribe(client, obj, mid, granted_qos):
    #Print when subscribed
    print("Subscribed! - "+str(mid)+" "+str(granted_qos))

#Run this command when Node-RED is sending a message on the subscribed topic
def on_message(client, userdata, msg):
    #Print the topic and the message
    print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
    #Update the global variables command, args and counter
    global command
    global args
    global counter
    #Parse the topic to find the command. ex : actuator/pump -> pump
    command=msg.topic.split("/")[1]
    #Decode the message to find the arguments
    args=str(msg.payload.decode())
    #Reset the counter to 0
    counter=0


################################################################################
#Init function - executed only once
################################################################################

#load config.json
import json

print("Started Reading JSON file")
with open("../config.json", "r") as config_file:
    configuration = json.load(config_file)


#define the names for the 2 exsting steppers
kit = MotorKit()
reverse = False
# check that the config file have the hardware_config and the stepper_reverse key
if 'hardware_config' in configuration:
    if 'stepper_reverse' in configuration['hardware_config']:
        reverse = configuration['hardware_config']['stepper_reverse']
if reverse:
    pump_stepper = kit.stepper2
    focus_stepper = kit.stepper1
else:
    pump_stepper = kit.stepper1
    focus_stepper = kit.stepper2

#Make sure the steppers are release and do not use any power
pump_stepper.release()
focus_stepper.release()

#Precise the settings of the PiCamera
camera = picamera.PiCamera()
camera.resolution = (3280, 2464)
camera.iso = 60
camera.shutter_speed = 500
camera.exposure_mode = 'fixedfps'

#Declare the global variables command, args and counter
command = ''
args = ''
counter=''

#MQTT Client functions definition
client = mqtt.Client()
client.connect("127.0.0.1",1883,60)
client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_message = on_message
client.loop_start()

################################################################################
#Definition of the few important metadata
################################################################################

local_metadata = {
    "process_datetime": datetime.now(),
    "acq_camera_resolution" : camera.resolution,
    "acq_camera_iso" : camera.iso,
    "acq_camera_shutter_speed" : camera.shutter_speed
}

#Read the content of config.json containing the metadata defined on Node-RED
config_json = open('/home/pi/PlanktonScope/config.json','r')
node_red_metadata = json.loads(config_json.read())

#Concat the local metadata and the metadata from Node-RED
global_metadata = {**local_metadata, **node_red_metadata}

#Define the name of the .zip file that will contain the images and the .tsv table for EcoTaxa
archive_fn = os.path.join("/home/pi/PlanktonScope/","export", "ecotaxa_export.zip")

################################################################################
#MorphoCut Script
################################################################################

#Define processing pipeline
with Pipeline() as p:

    #Recursively find .jpg files in import_path.
    #Sort to get consective frames.
    abs_path = Find("/home/pi/PlanktonScope/tmp", [".jpg"], sort=True, verbose=True)

    #Extract name from abs_path
    name = Call(lambda p: os.path.splitext(os.path.basename(p))[0], abs_path)

    #Set the LEDs as Green
    Call(planktonscope.light.setRGB, 0,255,0)

    #Read image
    img = ImageReader(abs_path)

    #Show progress bar for frames
    TQDM(Format("Frame {name}", name=name))

    #Apply running median to approximate the background image
    flat_field = RunningMedian(img, 5)

    #Correct image
    img = img / flat_field

    #Rescale intensities and convert to uint8 to speed up calculations
    img = RescaleIntensity(img, in_range=(0, 1.1), dtype="uint8")

    #Filter variable to reduce memory load
    FilterVariables(name,img)

    #Save cleaned images
    #frame_fn = Format(os.path.join("/home/pi/PlanktonScope/tmp","CLEAN", "{name}.jpg"), name=name)
    #ImageWriter(frame_fn, img)

    #Convert image to uint8 gray
    img_gray = RGB2Gray(img)

    #?
    img_gray = Call(img_as_ubyte, img_gray)

    #Canny edge detection using OpenCV
    img_canny = Call(cv2.Canny, img_gray, 50,100)

    #Dilate using OpenCV
    kernel = Call(cv2.getStructuringElement, cv2.MORPH_ELLIPSE, (15, 15))
    img_dilate = Call(cv2.dilate, img_canny, kernel, iterations=2)

    #Close using OpenCV
    kernel = Call(cv2.getStructuringElement, cv2.MORPH_ELLIPSE, (5, 5))
    img_close = Call(cv2.morphologyEx, img_dilate, cv2.MORPH_CLOSE, kernel, iterations=1)

    #Erode using OpenCV
    kernel = Call(cv2.getStructuringElement, cv2.MORPH_ELLIPSE, (15, 15))
    mask = Call(cv2.erode, img_close, kernel, iterations=2)

    #Find objects
    regionprops = FindRegions(
        mask, img_gray, min_area=1000, padding=10, warn_empty=name
    )

    #Set the LEDs as Purple
    Call(planktonscope.light.setRGB, 255,0,255)

    # For an object, extract a vignette/ROI from the image
    roi_orig = ExtractROI(img, regionprops, bg_color=255)

    # Generate an object identifier
    i = Enumerate()

    #Call(print,i)

    #Define the ID of each object
    object_id = Format("{name}_{i:d}", name=name, i=i)

    #Call(print,object_id)

    #Define the name of each object
    object_fn = Format(os.path.join("/home/pi/PlanktonScope/","OBJECTS", "{name}.jpg"), name=object_id)

    #Save the image of the object with its name
    ImageWriter(object_fn, roi_orig)

    #Calculate features. The calculated features are added to the global_metadata.
    #Returns a Variable representing a dict for every object in the stream.
    meta = CalculateZooProcessFeatures(
        regionprops, prefix="object_", meta=global_metadata
    )

    #Get all the metadata
    json_meta = Call(json.dumps,meta, sort_keys=True, default=str)

    #Publish the json containing all the metadata to via MQTT to Node-RED
    Call(client.publish, "receiver/segmentation/metric", json_meta)

    #Add object_id to the metadata dictionary
    meta["object_id"] = object_id

    #Generate object filenames
    orig_fn = Format("{object_id}.jpg", object_id=object_id)

    #Write objects to an EcoTaxa archive:
    #roi image in original color, roi image in grayscale, metadata associated with each object
    EcotaxaWriter(archive_fn, (orig_fn, roi_orig), meta)

    #Progress bar for objects
    TQDM(Format("Object {object_id}", object_id=object_id))

    #Publish the object_id to via MQTT to Node-RED
    Call(client.publish, "receiver/segmentation/object_id", object_id)

    #Set the LEDs as Green
    Call(planktonscope.light.setRGB, 0,255,0)

################################################################################
#While loop for capting commands from Node-RED
################################################################################

output = StreamingOutput()
address = ('', 8000)
server = StreamingServer(address, StreamingHandler)
threading.Thread(target=server.serve_forever).start()
camera.start_recording(output, format='mjpeg', resize=(640, 480))

while True:

    ############################################################################
    #Pump Event
    ############################################################################

    #If the command is "pump"
    if (command=="pump"):

        #Set the LEDs as Blue
        planktonscope.light.setRGB(0,0,255)

        #Get direction from the different received arguments
        direction=args.split(" ")[0]

        #Get delay (in between steps) from the different received arguments
        delay=float(args.split(" ")[1])

        #Get number of steps from the different received arguments
        nb_step=int(args.split(" ")[2])

        #Print status
        print("The pump has been started.")

        #Publish the status "Start" to via MQTT to Node-RED
        client.publish("receiver/pump", "Start");

        ########################################################################
        while True:

            #Depending on direction, select the right direction for the pump
            if direction == "BACKWARD":
                direction=stepper.BACKWARD

            if direction == "FORWARD":
                direction=stepper.FORWARD

            #Actuate the pump for one step in the right direction
            pump_stepper.onestep(direction=direction, style=stepper.DOUBLE)

            #Increment the counter
            counter+=1

            #Wait during the delay to pump at the right flowrate
            sleep(delay)

            ####################################################################
            #If counter reach the number of step, break
            if counter>nb_step:

                #Release the pump stepper to stop power draw
                pump_stepper.release()

                #Print status
                print("The pumping is done.")

                #Change the command to not re-enter in this while loop
                command="wait"

                #Publish the status "Done" to via MQTT to Node-RED
                client.publish("receiver/pump", "Done");

                #Set the LEDs as Green
                planktonscope.light.setRGB(0,255,0)

                #Reset the counter to 0
                counter=0

                break

            ####################################################################
            #If a new received command isn't "pump", break this while loop
            if command!="pump":

                #Release the pump stepper to stop power draw
                pump_stepper.release()

                #Print status
                print("The pump has been interrompted.")

                #Publish the status "Interrompted" to via MQTT to Node-RED
                client.publish("receiver/pump", "Interrompted");

                #Set the LEDs as Green
                planktonscope.light.setRGB(0,255,0)

                #Reset the counter to 0
                counter=0

                break

    ############################################################################
    #Focus Event
    ############################################################################

    #If the command is "focus"
    elif (command=="focus"):

        #Set the LEDs as Yellow
        planktonscope.light.setRGB(255,255,0)

        #Get direction from the different received arguments
        direction=args.split(" ")[0]

        #Get number of steps from the different received arguments
        nb_step=int(args.split(" ")[1])

        #Print status
        print("The focus has been started.")

        #Publish the status "Start" to via MQTT to Node-RED
        client.publish("receiver/focus", "Start");

        ########################################################################
        while True:

            #Depending on direction, select the right direction for the focus
            if direction == "FORWARD":
                direction=stepper.FORWARD

            if direction == "BACKWARD":
                direction=stepper.BACKWARD

            #Actuate the focus for one microstep in the right direction
            focus_stepper.onestep(direction=direction, style=stepper.MICROSTEP)

            #Increment the counter
            counter+=1

            ####################################################################
            #If counter reach the number of step, break
            if counter>nb_step:

                #Release the focus steppers to stop power draw
                focus_stepper.release()

                #Print status
                print("The focusing is done.")

                #Change the command to not re-enter in this while loop
                command="wait"

                #Publish the status "Done" to via MQTT to Node-RED
                client.publish("receiver/focus", "Done");

                #Set the LEDs as Green
                planktonscope.light.setRGB(0,255,0)

                #Reset the counter to 0
                counter=0

                break

            ####################################################################
            #If a new received command isn't "pump", break this while loop
            if command!="focus":

                #Release the focus steppers to stop power draw
                focus_stepper.release()

                #Print status
                print("The stage has been interrompted.")

                #Publish the status "Done" to via MQTT to Node-RED
                client.publish("receiver/focus", "Interrompted");

                #Set the LEDs as Green
                planktonscope.light.setRGB(0,255,0)

                #Reset the counter to 0
                counter=0

                break

    ############################################################################
    #Image Event
    ############################################################################

    elif (command=="image"):

        #Publish the status "Start" to via MQTT to Node-RED
        client.publish("receiver/image", "Will do my best dude");

        #Get duration to wait before an image from the different received arguments
        sleep_before=int(args.split(" ")[0])

        #Get number of step in between two images from the different received arguments
        nb_step=int(args.split(" ")[1])

        #Get the number of frames to image from the different received arguments
        nb_frame=int(args.split(" ")[2])

        #Get the segmentation status (true/false) from the different received arguments
        segmentation=str(args.split(" ")[3])

        #Sleep a duration before to start acquisition
        sleep(sleep_before)

        #Publish the status "Start" to via MQTT to Node-RED
        client.publish("receiver/image", "Start");

        #Set the LEDs as Blue
        planktonscope.light.setRGB(0,0,255)

        #Pump duing a given number of steps (in between each image)
        for i in range(nb_step):

            #If the command is still image - pump a defined nb of steps
            if (command=="image"):

                #Actuate the pump for one step in the FORWARD direction
                pump_stepper.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)

                #The flowrate is fixed for now.
                sleep(0.01)

            #If the command isn't image anymore - break
            else:

                break

        #Set the LEDs as Green
        planktonscope.light.setRGB(0,255,0)

        while True:

            #Set the LEDs as Cyan
            planktonscope.light.setRGB(0,255,255)

            #Increment the counter
            counter+=1

            #Get datetime
            datetime_tmp=datetime.now().strftime("%H_%M_%S_%f")

            #Print datetime
            print(datetime_tmp)

            #Define the filename of the image
            filename = os.path.join("/home/pi/PlanktonScope/tmp",datetime_tmp+".jpg")

            #Capture an image with the proper filename
            camera.capture(filename)

            #Set the LEDs as Green
            planktonscope.light.setRGB(0,255,0)

            #Publish the name of the image to via MQTT to Node-RED

            client.publish("receiver/image", datetime_tmp+".jpg has been imaged.");

            #Set the LEDs as Blue
            planktonscope.light.setRGB(0,0,255)

            #Pump during a given nb of steps
            for i in range(nb_step):

                #Actuate the pump for one step in the FORWARD direction
                pump_stepper.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)

                #The flowrate is fixed for now.
                sleep(0.01)

            #Wait a fixed delay which set the framerate as < than 2 imag/sec
            sleep(0.5)

            #Set the LEDs as Green
            planktonscope.light.setRGB(0,255,0)

            ####################################################################
            #If counter reach the number of frame, break
            if(counter>nb_frame):

                #Publish the status "Completed" to via MQTT to Node-RED
                client.publish("receiver/image", "Completed");

                #Release the pump steppers to stop power draw
                pump_stepper.release()

                if(segmentation == "True"):

                    #Publish the status "Start" to via MQTT to Node-RED
                    client.publish("receiver/segmentation", "Start");

                    #Start the MorphoCut Pipeline
                    p.run()

                    #remove directory
                    #shutil.rmtree(import_path)

                    #Publish the status "Completed" to via MQTT to Node-RED
                    client.publish("receiver/segmentation", "Completed");

                    #Set the LEDs as White
                    planktonscope.light.setRGB(255,255,255)

                    #cmd = os.popen("rm -rf /home/pi/PlanktonScope/tmp/*.jpg")

                    #Let it happen
                    sleep(1)

                    #Set the LEDs as Green
                    planktonscope.light.setRGB(0,255,0)

                    #End if(segmentation == "True"):

                #Change the command to not re-enter in this while loop
                command="wait"

                #Set the LEDs as Green
                planktonscope.light.setRGB(0,255,255)

                #Reset the counter to 0
                counter=0

                break

            ####################################################################
            #If a new received command isn't "image", break this while loop
            if command!="image":

                #Release the pump steppers to stop power draw
                pump_stepper.release()

                #Print status
                print("The imaging has been interrompted.")

                #Publish the status "Interrompted" to via MQTT to Node-RED
                client.publish("receiver/image", "Interrompted");

                #Set the LEDs as Green
                planktonscope.light.setRGB(0,255,0)

                #Reset the counter to 0
                counter=0

                break

    else:
        #Set the LEDs as Black
        planktonscope.light.setRGB(0,0,0)
        #Its just waiting to receive command from Node-RED
        sleep(1)
        #Set the LEDs as White
        planktonscope.light.setRGB(255,255,255)
        #Its just waiting to receive command from Node-RED
        sleep(1)
