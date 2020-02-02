import paho.mqtt.client as mqtt
from picamera import PiCamera
from datetime import datetime, timedelta
from adafruit_motor import stepper
from adafruit_motorkit import MotorKit
from time import sleep
import json

import os
import subprocess

from skimage.util import img_as_ubyte

from morphocut import Call
from morphocut.contrib.ecotaxa import EcotaxaWriter
from morphocut.contrib.zooprocess import CalculateZooProcessFeatures
from morphocut.core import Pipeline
from morphocut.file import Find
from morphocut.image import (
    ExtractROI,
    FindRegions,
    ImageReader,
    ImageWriter,
    RescaleIntensity,
    RGB2Gray,
)

from morphocut.stat import RunningMedian
from morphocut.str import Format
from morphocut.stream import TQDM, Enumerate, FilterVariables

from skimage.feature import canny
from skimage.color import rgb2gray, label2rgb
from skimage.morphology import disk
from skimage.morphology import erosion, dilation, closing
from skimage.measure import label, regionprops
import cv2, shutil

import smbus
#fan
bus = smbus.SMBus(1)
################################################################################
kit = MotorKit()
pump_stepper = kit.stepper1
pump_stepper.release()
focus_stepper = kit.stepper2
focus_stepper.release()

################################################################################

camera = PiCamera()
camera.resolution = (3280, 2464)
camera.iso = 60
camera.shutter_speed = 500
camera.exposure_mode = 'fixedfps'

################################################################################
message = ''
topic = ''
count=''

################################################################################

def on_connect(client, userdata, flags, rc):
    print("Connected! - " + str(rc))
    client.subscribe("actuator/#")
    rgb(0,255,0)
def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed! - "+str(mid)+" "+str(granted_qos))
    
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
    global message
    global topic
    global count
    message=str(msg.payload.decode())
    topic=msg.topic.split("/")[1]   
    count=0
    
def on_log(client, obj, level, string):
    print(string)

def rgb(R,G,B):
    bus.write_byte_data(0x0d, 0x00, 0)
    bus.write_byte_data(0x0d, 0x01, R)
    bus.write_byte_data(0x0d, 0x02, G)
    bus.write_byte_data(0x0d, 0x03, B)

    bus.write_byte_data(0x0d, 0x00, 1)
    bus.write_byte_data(0x0d, 0x01, R)
    bus.write_byte_data(0x0d, 0x02, G)
    bus.write_byte_data(0x0d, 0x03, B)

    bus.write_byte_data(0x0d, 0x00, 2)
    bus.write_byte_data(0x0d, 0x01, R)
    bus.write_byte_data(0x0d, 0x02, G)
    bus.write_byte_data(0x0d, 0x03, B)
    cmd="i2cdetect -y 1"
    subprocess.Popen(cmd.split(),stdout=subprocess.PIPE)
    
################################################################################
client = mqtt.Client()
client.connect("127.0.0.1",1883,60)
client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_log = on_log
client.loop_start() 


################################################################################
while True:
    
################################################################################
    if (topic=="pump"):
        rgb(0,0,255)
        direction=message.split(" ")[0]
        delay=float(message.split(" ")[1])
        nb_step=int(message.split(" ")[2])
        
        client.publish("receiver/pump", "Start");
        
            
        while True:
                
            if direction == "BACKWARD":
                direction=stepper.BACKWARD
            if direction == "FORWARD":
                direction=stepper.FORWARD
            count+=1
#             print(count,nb_step)
            pump_stepper.onestep(direction=direction, style=stepper.DOUBLE)
            sleep(delay)
            
            if topic!="pump":
                pump_stepper.release()
                print("The pump has been interrompted.")
                client.publish("receiver/pump", "Interrompted");
                rgb(0,255,0)
                break
            
            if count>nb_step:
                pump_stepper.release()
                print("The pumping is done.")
                topic="wait"
                client.publish("receiver/pump", "Done");
                rgb(0,255,0)
                break

################################################################################

    elif (topic=="focus"):
        
        rgb(255,255,0)
        direction=message.split(" ")[0]
        nb_step=int(message.split(" ")[1])
        client.publish("receiver/focus", "Start");
        
            
        while True:
            
            if direction == "FORWARD":
                direction=stepper.FORWARD
            if direction == "BACKWARD":
                direction=stepper.BACKWARD
            count+=1
#             print(count,nb_step)
            focus_stepper.onestep(direction=direction, style=stepper.MICROSTEP)
            
            if topic!="focus":
                focus_stepper.release()
                print("The stage has been interrompted.")
                client.publish("receiver/focus", "Interrompted");
                rgb(0,255,0)
                break
            
            if count>nb_step:
                focus_stepper.release()
                print("The focusing is done.")
                topic="wait"
                client.publish("receiver/focus", "Done");
                rgb(0,255,0)
                break

################################################################################
           
    elif (topic=="image"):
        
        camera.start_preview(fullscreen=False, window = (160, 0, 640, 480))
        
        sleep_before=int(message.split(" ")[0])
        
        nb_step=int(message.split(" ")[1])
        
        path=str(message.split(" ")[2])
        
        nb_frame=int(message.split(" ")[3])
        
        sleep_during=int(message.split(" ")[4])
        
        #sleep a duration before to start
        sleep(sleep_before)
        
        client.publish("receiver/image", "Start");
        
        #flushing before to begin
         
        rgb(0,0,255)
        for i in range(nb_step):
            pump_stepper.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
            sleep(0.01)
        rgb(0,255,0)
            
        directory = os.path.join(path, "PlanktonScope")
        os.makedirs(directory, exist_ok=True)
        
        export = os.path.join(directory, "export")
        os.makedirs(export, exist_ok=True)
        
        date=datetime.now().strftime("%m_%d_%Y")
        time=datetime.now().strftime("%H_%M")
        
        path_date = os.path.join(directory, date)
        os.makedirs(path_date, exist_ok=True)
        
        path_time = os.path.join(path_date,time)
        os.makedirs(path_time, exist_ok=True)
        while True:
            
            count+=1
#             print(count,nb_frame)
            
            filename = os.path.join(path_time,datetime.now().strftime("%M_%S_%f")+".jpg")
            
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
            
            if(count>nb_frame):
                
                camera.stop_preview()
                
                client.publish("receiver/image", "Completed");
                # Meta data that is added to every object
                local_metadata = {
                    "process_datetime": datetime.now(),
                    "acq_camera_resolution" : camera.resolution,
                    "acq_camera_iso" : camera.iso,
                    "acq_camera_shutter_speed" : camera.shutter_speed
                }
                global_metadata = None
                config_txt = None
                RAW = None
                CLEAN = None
                ANNOTATED = None
                OBJECTS = None
                archive_fn = None
                
                config_txt = open('/home/pi/PlanktonScope/config.txt','r') 
                node_red_metadata = json.loads(config_txt.read())

                global_metadata = {**local_metadata, **node_red_metadata}
                
                RAW = os.path.join(path_time, "RAW")
                os.makedirs(RAW, exist_ok=True)
                
                os.system("mv "+str(path_time)+"/*.jpg "+str(RAW))

                CLEAN = os.path.join(path_time, "CLEAN")
                os.makedirs(CLEAN, exist_ok=True)
                
                ANNOTATED = os.path.join(path_time, "ANNOTATED")
                os.makedirs(ANNOTATED, exist_ok=True)

                OBJECTS = os.path.join(path_time, "OBJECTS")
                os.makedirs(OBJECTS, exist_ok=True)

                archive_fn = os.path.join(directory,"export", str(date)+"_"+str(time)+"_ecotaxa_export.zip")

                client.publish("receiver/segmentation", "Start");
                # Define processing pipeline
                                # Define processing pipeline
                with Pipeline() as p:
                    # Recursively find .jpg files in import_path.
                    # Sort to get consective frames.
                    abs_path = Find(RAW, [".jpg"], sort=True, verbose=True)
                    
                    FilterVariables(abs_path)

                    # Extract name from abs_path
                    name = Call(lambda p: os.path.splitext(os.path.basename(p))[0], abs_path)

                    Call(rgb, 0,255,0)
                    # Read image
                    img = ImageReader(abs_path)

                    # Show progress bar for frames
                    #TQDM(Format("Frame {name}", name=name))
                    
                    # Apply running median to approximate the background image
                    flat_field = RunningMedian(img, 5)

                    # Correct image
                    img = img / flat_field
                    
                    FilterVariables(name,img)
                    
                    # Rescale intensities and convert to uint8 to speed up calculations
                    img = RescaleIntensity(img, in_range=(0, 1.1), dtype="uint8")
                    
                    frame_fn = Format(os.path.join(CLEAN, "{name}.jpg"), name=name)
                    
                    ImageWriter(frame_fn, img)
                    
                    FilterVariables(name,img)
                    
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
                    
                    FilterVariables(name,img,img_gray,mask)
                    
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
                    
                    object_fn = Format(os.path.join(OBJECTS, "{name}.jpg"), name=object_id)
                    
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

                    FilterVariables(orig_fn,roi_orig,meta,object_id)
                    # Write objects to an EcoTaxa archive:
                    # roi image in original color, roi image in grayscale, metadata associated with each object
                    EcotaxaWriter(archive_fn, (orig_fn, roi_orig), meta)

                    # Progress bar for objects
                    TQDM(Format("Object {object_id}", object_id=object_id))
                                    
                    Call(client.publish, "receiver/segmentation/object_id", object_id)
                    
                    meta=None
                    FilterVariables(meta)
                    

                p.run()
                
                #remove directory
                #shutil.rmtree(import_path)
                
                client.publish("receiver/segmentation", "Completed");
                
                rgb(255,255,255)
                sleep(sleep_during)
                rgb(0,255,0)
                
                date=datetime.now().strftime("%m_%d_%Y")
                time=datetime.now().strftime("%H_%M")
                
                path_date = os.path.join(directory, date)
                os.makedirs(path_date, exist_ok=True)
                
                path_time = os.path.join(path_date,time)
                os.makedirs(path_time, exist_ok=True)
                
                rgb(0,0,255)
                for i in range(nb_step):
                    pump_stepper.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
                    sleep(0.01)
                rgb(0,255,0)
                
                os.makedirs(path_time, exist_ok=True)
                count=0
                
            if topic!="image":
                pump_stepper.release()
                print("The imaging has been interrompted.")
                client.publish("receiver/image", "Interrompted");
                rgb(0,255,0)
                count=0
                break
            
    else:
#         print("Waiting")
        sleep(1)


