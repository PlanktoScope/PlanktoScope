import paho.mqtt.client as mqtt
from picamera import PiCamera
from datetime import datetime, timedelta
from adafruit_motor import stepper
from adafruit_motorkit import MotorKit
from time import sleep

import json

import os

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
from morphocut.stream import TQDM, Enumerate

from skimage.feature import canny
from skimage.color import rgb2gray, label2rgb
from skimage.morphology import disk
from skimage.morphology import erosion, dilation, closing
from skimage.measure import label, regionprops

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
sleep(3)
camera.shutter_speed = 100
camera.exposure_mode = 'off'
g = camera.awb_gains
camera.awb_mode = 'off'
camera.awb_gains = g
nb_frame=200

################################################################################
message = ''
topic = ''
count=''

################################################################################

def on_connect(client, userdata, flags, rc):
  print("Connected! - " + str(rc))
  client.subscribe("actuator/#")

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
        
        direction=message.split(" ")[0]
        delay=float(message.split(" ")[1])
        nb_step=int(message.split(" ")[2])
        
        client.publish("receiver/pump", "Start");
        
        if direction == "BACKWARD":
            direction=stepper.direction
        if direction == "FORWARD":
            direction=stepper.FORWARD
            
        while True:
            count+=1
            print(count,nb_step)
            pump_stepper.onestep(direction=direction, style=stepper.DOUBLE)
            sleep(delay)
            
            if topic!="pump":
                pump_stepper.release()
                print("The pump has been interrompted.")
                client.publish("receiver/pump", "Interrompted");
                break
            
            if count>nb_step:
                pump_stepper.release()
                print("The pumping is done.")
                topic="wait"
                client.publish("receiver/pump", "Done");
                break

################################################################################

    elif (topic=="focus"):
        
        direction=message.split(" ")[0]
        nb_step=int(message.split(" ")[1])
        client.publish("receiver/focus", "Start");
        
        if direction == "FORWARD":
            direction=stepper.FORWARD
        if direction == "BACKWARD":
            direction=stepper.BACKWARD
            
        while True:
            count+=1
            print(count,nb_step)
            focus_stepper.onestep(direction=direction, style=stepper.MICROSTEP)
            
            
            if topic!="focus":
                focus_stepper.release()
                print("The stage has been interrompted.")
                client.publish("receiver/focus", "Interrompted");
                break
            
            if count>nb_step:
                focus_stepper.release()
                print("The focusing is done.")
                topic="wait"
                client.publish("receiver/focus", "Done");
                break

################################################################################
           
    elif (topic=="image"):
        
        sleep_before=int(message.split(" ")[0])
        
        nb_step=int(message.split(" ")[1])
        
        path=str(message.split(" ")[2])
        
        nb_frame=int(message.split(" ")[3])
        
        sleep_during=int(message.split(" ")[4])
        
        #sleep a duration before to start
        sleep(sleep_before)
        
        client.publish("receiver/image", "Start");
        
        #flushing before to begin
        
        for i in range(nb_step):
            pump_stepper.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
            sleep(0.01)
            
        directory = os.path.join(path, "PlanktonScope")
        os.makedirs(directory, exist_ok=True)
        
        date=datetime.now().strftime("%m_%d_%Y")
        time=datetime.now().strftime("%H_%M")
        
        path_date = os.path.join(directory, date)
        os.makedirs(path_date, exist_ok=True)
        
        
        path_time = os.path.join(path_date,time)
        
        os.makedirs(path_time, exist_ok=True)
        
        while True:
            count+=1
            print(count,nb_frame)
            
            filename = os.path.join(path_time,datetime.now().strftime("%M_%S_%f")+".jpg")
            camera.capture(filename)
            client.publish("receiver/image", datetime.now().strftime("%M_%S_%f")+".jpg has been imaged.");

            for i in range(10):
                pump_stepper.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
                sleep(0.01)
            sleep(0.5)
            
            if(count>nb_frame):
                # Meta data that is added to every object
                local_metadata = {
                    "process_datetime": datetime.now(),
                    "acq_camera_resolution" : camera.resolution,
                    "acq_camera_iso" : camera.iso,
                    "acq_camera_shutter_speed" : camera.shutter_speed
                }

                config_txt = open('/home/pi/PlanktonScope/config.txt','r') 
                node_red_metadata = json.loads(config_txt.read())

                global_metadata = {**local_metadata, **node_red_metadata}

                import_path = path_time
                archive_fn = os.path.join(directory, str(date)+"_"+str(time)+"_ecotaxa_export.zip")

                # Define processing pipeline
                with Pipeline() as p:
                    # Recursively find .jpg files in import_path.
                    # Sort to get consective frames.
                    abs_path = Find(import_path, [".jpg"], sort=True, verbose=True)

                    # Extract name from abs_path
                    name = Call(lambda p: os.path.splitext(os.path.basename(p))[0], abs_path)

                    # Read image
                    img = ImageReader(abs_path)

                    # Apply running median to approximate the background image
                    flat_field = RunningMedian(img, 5)
                    
                    # Correct image
                    img = img / flat_field
                    
                    # Rescale intensities and convert to uint8 to speed up calculations
                    img = RescaleIntensity(img, in_range=(0, 1.1), dtype="uint8")

                    # Convert image to uint8 gray
                    img_gray = RGB2Gray(img)

                    img_gray = Call(img_as_ubyte, img_gray)

                    img_canny = Call(canny, img_gray, sigma=0.3)

                    img_dilate = Call(dilation, img_canny)

                    img_closing = Call(closing, img_dilate)

                    mask = Call(erosion, img_closing)

                    # Show progress bar for frames
                    TQDM(Format("Frame {name}", name=name))
                    
                    # Apply threshold find objects
                    #threshold = 204  # Call(skimage.filters.threshold_otsu, img_gray)
                    #mask = img_gray < threshold

                    # Find objects
                    regionprops = FindRegions(
                        mask, img_gray, min_area=1000, padding=10, warn_empty=name
                    )

                    # For an object, extract a vignette/ROI from the image
                    roi_orig = ExtractROI(img, regionprops, bg_color=255)

                    roi_orig
                    # Generate an object identifier
                    i = Enumerate()
                    #Call(print,i)

                    object_id = Format("{name}_{i:d}", name=name, i=i)
                    #Call(print,object_id)


                    # Calculate features. The calculated features are added to the global_metadata.
                    # Returns a Variable representing a dict for every object in the stream.
                    meta = CalculateZooProcessFeatures(
                        regionprops, prefix="object_", meta=global_metadata
                    )
                    # If CalculateZooProcessFeatures is not used, we need to copy global_metadata into the stream:
                    # meta = Call(lambda: global_metadata.copy())
                    # https://github.com/morphocut/morphocut/issues/51

                    # Add object_id to the metadata dictionary
                    meta["object_id"] = object_id

                    # Generate object filenames
                    orig_fn = Format("{object_id}.jpg", object_id=object_id)

                    # Write objects to an EcoTaxa archive:
                    # roi image in original color, roi image in grayscale, metadata associated with each object
                    EcotaxaWriter(archive_fn, (orig_fn, roi_orig), meta)

                    # Progress bar for objects
                    TQDM(Format("Object {object_id}", object_id=object_id))
                    
                    Call(client.publish, "receiver/image", object_id)

                p.run() 
                sleep(sleep_during)
                
                count=0
                
                for i in range(nb_step):
                    pump_stepper.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
                    sleep(0.01)
                
            if topic!="image":
                pump_focus.release()
                print("The imaging has been interrompted.")
                client.publish("receiver/image", "Interrompted");
                break
            
    else:
        print("Waiting")
        sleep(1)


