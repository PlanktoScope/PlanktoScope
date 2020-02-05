################################################################################
#Actuator Libraries
################################################################################

#Library for exchaning messages with Node-RED
import paho.mqtt.client as mqtt

#Library to control the PiCamera
from picamera import PiCamera

#Libraries to control the steppers for focusing and pumping
from adafruit_motor import stepper
from adafruit_motorkit import MotorKit

#Library to send command over I2C for the light module on the fan
import smbus

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
#pip3 install opencv-python
import cv2


################################################################################
#STREAMING
################################################################################
import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server
import threading

PAGE="""\
<html>
<head>
<title>picamera MJPEG streaming demo</title>
</head>
<body>
<img src="stream.mjpg" width="640" height="480" />
</body>
</html>
"""

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
    rgb(0,255,0)

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
#Actuators core functions
################################################################################
def rgb(R,G,B):
    #Update LED n°1
    bus.write_byte_data(0x0d, 0x00, 0)
    bus.write_byte_data(0x0d, 0x01, R)
    bus.write_byte_data(0x0d, 0x02, G)
    bus.write_byte_data(0x0d, 0x03, B)

    #Update LED n°2
    bus.write_byte_data(0x0d, 0x00, 1)
    bus.write_byte_data(0x0d, 0x01, R)
    bus.write_byte_data(0x0d, 0x02, G)
    bus.write_byte_data(0x0d, 0x03, B)

    #Update LED n°3
    bus.write_byte_data(0x0d, 0x00, 2)
    bus.write_byte_data(0x0d, 0x01, R)
    bus.write_byte_data(0x0d, 0x02, G)
    bus.write_byte_data(0x0d, 0x03, B)

    #Update the I2C Bus in order to really update the LEDs new values
    cmd="i2cdetect -y 1"
    subprocess.Popen(cmd.split(),stdout=subprocess.PIPE)



################################################################################
#Init function - executed only once
################################################################################

#define the bus used to actuate the light module on the fan
bus = smbus.SMBus(1)

#define the names for the 2 exsting steppers
kit = MotorKit()
pump_stepper = kit.stepper1
pump_stepper.release()
focus_stepper = kit.stepper2
focus_stepper.release()

#Precise the settings of the PiCamera
camera = PiCamera()
camera.resolution = (3280, 2464)
camera.iso = 60
camera.shutter_speed = 500
camera.exposure_mode = 'fixedfps'

#Declare the global variables command, args and counter
command = ''
args = ''
counter=''

client = mqtt.Client()
client.connect("127.0.0.1",1883,60)
client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_message = on_message
client.loop_start()

################################################################################

local_metadata = {
    "process_datetime": datetime.now(),
    "acq_camera_resolution" : camera.resolution,
    "acq_camera_iso" : camera.iso,
    "acq_camera_shutter_speed" : camera.shutter_speed
}

config_txt = open('/home/pi/PlanktonScope/config.txt','r')
node_red_metadata = json.loads(config_txt.read())

global_metadata = {**local_metadata, **node_red_metadata}

archive_fn = os.path.join("/home/pi/PlanktonScope/","export", "ecotaxa_export.zip")
# Define processing pipeline

with Pipeline() as p:
    # Recursively find .jpg files in import_path.
    # Sort to get consective frames.
    abs_path = Find("/home/pi/PlanktonScope/tmp", [".jpg"], sort=True, verbose=True)


    # Extract name from abs_path
    name = Call(lambda p: os.path.splitext(os.path.basename(p))[0], abs_path)

    Call(rgb, 0,255,0)

    # Read image
    img = ImageReader(abs_path)

    # Show progress bar for frames
    TQDM(Format("Frame {name}", name=name))

    # Apply running median to approximate the background image
    flat_field = RunningMedian(img, 5)

    # Correct image
    img = img / flat_field

    # Rescale intensities and convert to uint8 to speed up calculations
    img = RescaleIntensity(img, in_range=(0, 1.1), dtype="uint8")

    FilterVariables(name,img)
#     frame_fn = Format(os.path.join("/home/pi/PlanktonScope/tmp","CLEAN", "{name}.jpg"), name=name)

#     ImageWriter(frame_fn, img)

    # Convert image to uint8 gray
    img_gray = RGB2Gray(img)

    # ?
    img_gray = Call(img_as_ubyte, img_gray)

    #Canny edge detection
    img_canny = Call(cv2.Canny, img_gray, 50,100)

    #Dilate
    kernel = Call(cv2.getStructuringElement, cv2.MORPH_ELLIPSE, (15, 15))
    img_dilate = Call(cv2.dilate, img_canny, kernel, iterations=2)

    #Close
    kernel = Call(cv2.getStructuringElement, cv2.MORPH_ELLIPSE, (5, 5))
    img_close = Call(cv2.morphologyEx, img_dilate, cv2.MORPH_CLOSE, kernel, iterations=1)

    #Erode
    kernel = Call(cv2.getStructuringElement, cv2.MORPH_ELLIPSE, (15, 15))
    mask = Call(cv2.erode, img_close, kernel, iterations=2)

    # Find objects
    regionprops = FindRegions(
        mask, img_gray, min_area=1000, padding=10, warn_empty=name
    )

    Call(rgb, 255,0,255)
    # For an object, extract a vignette/ROI from the image
    roi_orig = ExtractROI(img, regionprops, bg_color=255)

    # Generate an object identifier
    i = Enumerate()
    #Call(print,i)

    object_id = Format("{name}_{i:d}", name=name, i=i)
    #Call(print,object_id)
    object_fn = Format(os.path.join("/home/pi/PlanktonScope/","OBJECTS", "{name}.jpg"), name=object_id)

    ImageWriter(object_fn, roi_orig)

    # Calculate features. The calculated features are added to the global_metadata.
    # Returns a Variable representing a dict for every object in the stream.
    meta = CalculateZooProcessFeatures(
        regionprops, prefix="object_", meta=global_metadata
    )

    json_meta = Call(json.dumps,meta, sort_keys=True, default=str)

    Call(client.publish, "receiver/segmentation/metric", json_meta)

    # Add object_id to the metadata dictionary
    meta["object_id"] = object_id

    # Generate object filenames
    orig_fn = Format("{object_id}.jpg", object_id=object_id)

    # Write objects to an EcoTaxa archive:
    # roi image in original color, roi image in grayscale, metadata associated with each object
    EcotaxaWriter(archive_fn, (orig_fn, roi_orig), meta)

    # Progress bar for objects
    TQDM(Format("Object {object_id}", object_id=object_id))

    Call(client.publish, "receiver/segmentation/object_id", object_id)


output = StreamingOutput()
address = ('', 8000)
server = StreamingServer(address, StreamingHandler)

threading.Thread(target=server.serve_forever).start()
################################################################################

camera.start_recording(output, format='mjpeg', resize=(640, 480))
while True:

    if (command=="pump"):
        rgb(0,0,255)
        direction=args.split(" ")[0]
        delay=float(args.split(" ")[1])
        nb_step=int(args.split(" ")[2])

        client.publish("receiver/pump", "Start");


        while True:

            if direction == "BACKWARD":
                direction=stepper.BACKWARD
            if direction == "FORWARD":
                direction=stepper.FORWARD
            pump_stepper.onestep(direction=direction, style=stepper.DOUBLE)
            counter+=1
            sleep(delay)

            if command!="pump":
                pump_stepper.release()
                print("The pump has been interrompted.")
                client.publish("receiver/pump", "Interrompted");
                rgb(0,255,0)
                break

            if counter>nb_step:
                pump_stepper.release()
                print("The pumping is done.")
                command="wait"
                client.publish("receiver/pump", "Done");
                rgb(0,255,0)
                break

################################################################################

    elif (command=="focus"):

        rgb(255,255,0)
        direction=args.split(" ")[0]
        nb_step=int(args.split(" ")[1])
        client.publish("receiver/focus", "Start");


        while True:

            if direction == "FORWARD":
                direction=stepper.FORWARD
            if direction == "BACKWARD":
                direction=stepper.BACKWARD
            counter+=1
            focus_stepper.onestep(direction=direction, style=stepper.MICROSTEP)

            if command!="focus":
                focus_stepper.release()
                print("The stage has been interrompted.")
                client.publish("receiver/focus", "Interrompted");
                rgb(0,255,0)
                break

            if counter>nb_step:
                focus_stepper.release()
                print("The focusing is done.")
                command="wait"
                client.publish("receiver/focus", "Done");
                rgb(0,255,0)
                break

################################################################################

    elif (command=="image"):


        sleep_before=int(args.split(" ")[0])

        nb_step=int(args.split(" ")[1])

        path=str(args.split(" ")[2])

        nb_frame=int(args.split(" ")[3])

        sleep_during=int(args.split(" ")[4])

        #sleep a duration before to start
        sleep(sleep_before)


        client.publish("receiver/image", "Start");

        #flushing before to begin

        rgb(0,0,255)
        for i in range(nb_step):
            if (command=="image"):
                pump_stepper.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
                sleep(0.01)
            else:
                break
        rgb(0,255,0)

        while True:

            counter+=1
            print(datetime.now().strftime("%H_%M_%S_%f"))
            filename = os.path.join("/home/pi/PlanktonScope/tmp",datetime.now().strftime("%M_%S_%f")+".jpg")

            rgb(0,255,255)
            camera.capture(filename)
            rgb(0,255,0)

            client.publish("receiver/image", datetime.now().strftime("%M_%S_%f")+".jpg has been imaged.");

            rgb(0,0,255)
            for i in range(10):
                pump_stepper.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
                sleep(0.01)
            sleep(0.5)
            rgb(0,255,0)

            if(counter>nb_frame):

#                 camera.stop_preview()

                client.publish("receiver/image", "Completed");
                # Meta data that is added to every object



                client.publish("receiver/segmentation", "Start");
                # Define processing pipeline


                p.run()

                #remove directory
                #shutil.rmtree(import_path)

                client.publish("receiver/segmentation", "Completed");


                cmd = os.popen("rm -rf /home/pi/PlanktonScope/tmp/*.jpg")

                rgb(255,255,255)
                sleep(sleep_during)
                rgb(0,255,0)


                rgb(0,0,255)
                for i in range(nb_step):
                    pump_stepper.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
                    sleep(0.01)
                rgb(0,255,0)

                counter=0


            if command!="image":
                pump_stepper.release()
                print("The imaging has been interrompted.")
                client.publish("receiver/image", "Interrompted");
                rgb(0,255,0)
                counter=0
                break

    else:
#         print("Waiting")
        sleep(1)
