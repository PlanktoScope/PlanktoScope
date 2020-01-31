import paho.mqtt.client as mqtt
from picamera import PiCamera
from datetime import datetime, timedelta
import os
from adafruit_motor import stepper
from adafruit_motorkit import MotorKit
from time import sleep

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
        flowrate=message.split(" ")[1]
        volume=message.split(" ")[2]
        nb_step=int(volume)*507
        duration=(int(volume)*60)/float(flowrate)
        delay=(duration/nb_step)-0.005
        client.publish("receiver/pump", "Start");
        
        while True:
            count+=1
            print(count,nb_step)
            print("pump_stepper.onestep(direction=+action+, style=stepper.DOUBLE")
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
        
        while True:
            count+=1
            print(count,nb_step)
            print("stage.onestep(direction=+action+, style=stepper.microstep")
            sleep(0.001)
            
            if topic!="focus":
                pump_focus.release()
                print("The stage has been interrompted.")
                client.publish("receiver/focus", "Interrompted");
                break
            
            if count>nb_step:
                pump_focus.release()
                print("The focusing is done.")
                topic="wait"
                client.publish("receiver/focus", "Done");
                break

################################################################################
           
    elif (topic=="image"):
        
        delay=int(message.split(" ")[0])
        volume_before=int(message.split(" ")[1])
        nb_frame=int(message.split(" ")[2])
        wait_duration=int(message.split(" ")[3])
        path=str(message.split(" ")[4])
        
        #sleep a duration before to start
        sleep(delay)
        
        client.publish("receiver/image", "Start");
        
        #flushing before to begin
        nb_step=int(volume)*507
        
        for i in range(nb_step):
            print("pump_stepper.onestep(direction=+action+, style=stepper.DOUBLE")
            time.sleep(0.01)
            
        directory = os.path.join(path, "PlanktonScope")
        os.makedirs(directory, exist_ok=True)
            
        
        path_date = os.path.join(directory, datetime.now().strftime("%m_%d_%Y"))
        os.makedirs(path_date, exist_ok=True)

        path_hour = os.path.join(path_date,datetime.now().strftime("%H"))
        os.makedirs(path_hour, exist_ok=True)
        
        while True:
            count+=1
            print(count,nb_frame)
            
            filename = os.path.join(path_hour,datetime.now().strftime("%M_%S_%f")+".jpg")
            camera.capture(filename)
            print("pump_stepper.onestep(direction=+action+, style=stepper.DOUBLE")

            if topic!="image":
                pump_focus.release()
                print("The imaging has been interrompted.")
                client.publish("receiver/image", "Interrompted");
                break
            
            if count>nb_frame:
                print("The imaging is done.")
                topic="wait"
                client.publish("receiver/image", "Done");
                break
        
    else:
        print("Waiting")
        sleep(1)
