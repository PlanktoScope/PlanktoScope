.. _install:

==========================
PlanktonScope Installation
==========================
Example of a subtitle following a header
    pi@raspberrypi:~/retext $ python3 retext.py

Install Raspbian on your Raspberry Pi
=====================================
Download the image
Download the .zip file of Raspbian Buster with desktop from the Raspberry Pi website Downloads page.

Writing an image to the SD card
Download the latest version of balenaEtcher and install it.
Connect an SD card reader with the micro SD card inside.
Open balenaEtcher and select from your hard drive the Raspberry Pi .zip file you wish to write to the SD card.
Select the SD card you wish to write your image to.
Review your selections and click 'Flash!' to begin writing data to the SD card.

Prepare your Raspberry Pi
https://projects.raspberrypi.org/en/projects/raspberry-pi-getting-started/
Plug the SD Card in your Raspberry Pi
Connect your Pi to a screen, mouse, keyboard and power 
Finish the setup

Install the needed libraries for the PlanktonScope
Make sure you have access to internet and update/upgrade your fresh raspbian
Update your Pi first::
    sudo apt-get update -y
    sudo apt-get upgrade -y

Reboot your Pi safely::
    sudo reboot now

Install CircuitPython
https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi 

Text
Type this command::
    sudo apt-get install python3-pip

Enable I2C and SPI
A vast number of our CircuitPython drivers use I2C and SPI for interfacing so you'll want to get those enabled.
You only have to do this once per Raspberry Pi but by default both interfaces are disabled!
Enable I2C
Enable SPI
Once you're done with both::
    sudo reboot now

Verify you have the I2C and SPI devices with the command::
    ls /dev/i2c* /dev/spi*

Run the following command to install adafruit_blinka::
    pip3 install adafruit-blinka

Install MotorKit
https://learn.adafruit.com/adafruit-dc-and-stepper-motor-hat-for-raspberry-pi?view=all 
Check I2C it is working::
    i2cdetect -y 1

Install Circuit Python::
    sudo pip3 install adafruit-circuitpython-motorkit

Install RPi Cam Web Interface
https://elinux.org/RPi-Cam-Web-Interface 
Attach the PiCamera to your Raspberry Pi
Enable Camera/SSH/I2C in raspi-config::
    sudo raspi-config

Reboot::
    sudo reboot now

Update your RPi::
    sudo apt-get update -y
    sudo apt-get upgrade -y

Reboot your Pi safely::
    sudo reboot now

Clone the code from github and enable and run the install script with the following commands::
    git clone https://github.com/silvanmelchior/RPi_Cam_Web_Interface.git
    cd RPi_Cam_Web_Interface
    ./install.sh

Press Enter to allow default setting of the installation
Press Enter to start RPi Cam Web Interface now
Found what is the IP of your Raspberry Pi::
    sudo ip addr show | grep 'inet 1'

Reach the url on a local browser : http://127.0.0.1/html/

Install Ultimate GPS HAT
Set up the Pi to release the console pins
https://learn.adafruit.com/adafruit-ultimate-gps-hat-for-raspberry-pi/pi-setup 
Run sudo raspi-config to open up the configuration page and select Interfacing Options :
Select Serial
Select NO
Keep the Serial Port Hardware enabled
Thats it!
Shutdown your Pi safely::
    sudo shutdown -h now


http://www.danmandle.com/blog/getting-gpsd-to-work-with-python/ 
Install RGB Cooling HAT
https://www.yahboom.net/study/RGB_Cooling_HAT 
https://github.com/YahboomTechnology/Raspberry-Pi-RGB-Cooling-HAT
Type this command::
    git clone https://github.com/WiringPi/WiringPi.git
    cd WiringPi
    sudo ./build
    sudo apt-get install gcc
    
Download temp_control.zip::
    Unzip it in /home/pi/
    cd temp_control/
    Uncomment all lines related to I2C led

//wiringPiI2CWriteReg8(fd_i2c, 0x04, 0x03);
//wiringPiI2CWriteReg8(fd_i2c, 0x04, 0x04);
//wiringPiI2CWriteReg8(fd_i2c, 0x04, 0x02);
//wiringPiI2CWriteReg8(fd_i2c, 0x04, 0x01);
//wiringPiI2CWriteReg8(fd_i2c, 0x04, 0x03);


    gcc -o temp_control temp_control.c ssd1306_i2c.c -lwiringPi


Install Node-RED
https://nodered.org/docs/getting-started/raspberrypi

Type this command::
    bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered)
 





Install MorphoCut
https://morphocut.readthedocs.io/en/stable/installation.html 
MorphoCut is packaged on PyPI and can be installed with pip::
    pip install morphocut

Install MorphoCut server
https://github.com/morphocut/morphocut-server 
Morphocut server requires Docker Compose, Nodejs and Conda
Docker Compose
Installing Docker
https://withblue.ink/2019/07/13/yes-you-can-run-docker-on-raspbian.html 
Installing Docker CE on Raspbian (Stretch or Buster) for Raspberry Pi is straightforward, and it’s fully supported by Docker. Docker CE is not supported on Raspbian Jessie anymore, so I’d recommend upgrading to a more recent release.
We’re going to install Docker from the official Docker repositories. While there are Docker packages on the Raspbian repos too, those are not kept up to date, which is something of an issue with a fast-evolving software like Docker.
To install Docker CE on Raspbian Stretch and Buster:
Install some required packages first
sudo apt update -y
sudo apt install -y apt-transport-https ca-certificates curl gnupg2 software-properties-common

Get the Docker signing key for packages
curl -fsSL https://download.docker.com/linux/$(. /etc/os-release; echo "$ID")/gpg | sudo apt-key add -

Add the Docker official repos
echo "deb [arch=armhf] https://download.docker.com/linux/$(. /etc/os-release; echo "$ID") \
     $(lsb_release -cs) stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list

The aufs package, part of the "recommended" packages, won't install on Buster just yet, because of missing pre-compiled kernel modules. We can work around that issue by using "--no-install-recommends"
sudo apt update
sudo apt install -y --no-install-recommends \
    docker-ce \
    cgroupfs-mount

That’s it! The next step is about starting Docker and enabling it at boot:
sudo systemctl enable docker
sudo systemctl start docker

Now that we have Docker running, we can test it by running the “hello world” image:
sudo docker run --rm arm32v7/hello-world

If everything is working fine, the command above will output something similar to:



About ARM images
This should hardly come as a surprise, but there’s a caveat with running Docker on a Raspberry Pi. Since those small devices do not run on x86_64, but rather have ARM-based CPUs, you won’t be able to use all the packages on the Docker Hub.
Instead, you need to look for images distributed by the arm32v7 organization (called armhf before), or tagged with those labels. Good news is that the arm32v7 organization is officially supported by Docker, so you get high-quality images.
While the CPUs inside Raspberry Pi 3’s and 4’s are using the ARMv8 (or ARM64) architecture, Raspbian is compiled as a 32-bit OS, so using Raspbian you’re not able to run 64-bit applications or containers.
Many common applications are already pre-built for ARM, including a growing number of official images, and you can also find a list of community-contributed arm32v7 images on Docker Hub. However, this is still a fraction of the number of images available for the x86_64 architecture.
Installing Docker Compose
In this last step we’re installing Docker Compose.
The official installation method for Linux, as in the Docker documentation, points users to the GitHub downloads page, which however does not offer pre-built binaries for the ARM architecture.
Luckily, we can still easily install Docker Compose from pip:
Install required packages
sudo apt update
sudo apt install -y python python-pip libffi-dev python-backports.ssl-match-hostname

Install Docker Compose from pip, this might take a while :
sudo pip install docker-compose

With this, you now have a complete Raspberry Pi mini-server running Docker and ready to accept your containers.
Nodejs
https://www.instructables.com/id/Install-Nodejs-and-Npm-on-Raspberry-Pi/ 
Conda
https://stackoverflow.com/questions/39371772/how-to-install-anaconda-on-raspberry-pi-3-model-b 
Go and get the latest version of miniconda for Raspberry Pi - made for armv7l processor and bundled with Python 3 (eg.: uname -m)
wget http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-armv7l.sh
md5sum Miniconda3-latest-Linux-armv7l.sh
bash Miniconda3-latest-Linux-armv7l.sh

After installation, source your updated .bashrc file with :
source ~/.bashrc

Then enter the command, 
python --version

which should give you :
Python 3.4.3 :: Continuum Analytics, Inc.

Install Jupyter Notebook
https://www.instructables.com/id/Jupyter-Notebook-on-Raspberry-Pi/ 
sudo su -
apt-get update
apt-get install python3-matplotlib
apt-get install python3-scipy
pip3 install --upgrade pip
reboot
sudo pip3 install jupyter

Script to realize an acquisition
Set color FAN HAT to init
Get a fix 
Set the pump to fast for x seconds
Set the pump to super slow
Set the focus manually
Click on start
Set the pump to normal flowrate
Set the picamera

Bill of Material
Items
Quantity
Price
µ-Slide I Luer Variety Pack
1
$120
M12 Lens Set
1
$60
Raspberry Pi 4 Model B
1
$62
Peristaltic Metering Pump with Stepper Motor
1
$60
Adafruit Ultimate GPS HAT Needs the antenna
1
$43
Adapter RMS to M12 x 0.5
1
$42
MicroSD Card 256GB
1
$28
Adafruit DC & Stepper Motor HAT
1
$27
Raspberry Pi Camera Module V2
1
$25
Linear Stepper Motor 12V Focus actuators
2
$20
Yahboom Cooling Fan Hat
1
$17
Adafruit GPS Antenna
1
$15
Power Supply 12V 2A
1
$10
Adafruit Power Supply 5.1V 3A - USB C
1
$10
Adafruit Hammer Header Male
1
$7
Adafruit GPIO Ribbon Cable
1
$3
Adafruit GPIO Stacking Header
1
$2
Female Mount Connector Jack Socket
1
$1
Switch Accessory, RJ45 Socket
1
$1
Standoff Male to Female 6mm - 2.5mm
8
$1
White LED 5mm Ultra Bright
1
$0
Standoff Male to Female 15mm - 2.5mm
8
$0
Machine Screw, M2.5
8
$0
6mm thick acrylic - 60cm x 30cm
1
$0





sudo apt-get update -y

sudo apt-get upgrade -y

sudo apt-get install gpsd gpsd-clients python-gps
-> not installed ion python3.7
pip3 install gps


//test to add the tiny HQ clock (useless if the GPS works)
sudo apt-get install gcc

git clone https://github.com/silvanmelchior/RPi_Cam_Web_Interface.git
cd RPi_Cam_Web_Interface/
./install.sh
./stop.sh

sudo pip3 install adafruit-circuitpython-motorkit

pip install morphocut
-> Could not find a version that satisfies the requirement morphocut (from versions: )
No matching distribution found for morphocut

pip3 install morphocut
-> not installed properly - Read timed out

sudo pip3 install morphocut
-> need a better internet

install morphocut server
wget http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-armv7l.sh
sudo md5sum Miniconda3-latest-Linux-armv7l.sh




















                             
acq_autoimage_rate
acq_camera_name
acq_celltype
acq_dsp_firmware
acq_end
acq_flash_delay
acq_flash_duration
acq_flow_cell_type
acq_fluid_volume_imaged
acq_id
acq_initialization
acq_instrument
acq_magnification
acq_max_esd
acq_min_esd
acq_mode
acq_raw_image_total
acq_recalibration_interval_minute
acq_sampling_time
acq_save_image_file
acq_serialno
acq_software
acq_start
acq_stop_reason
acq_threshold_black
Acq_threshold_light


object_%area
object_angle
object_area
object_area_exc
object_bx
object_by
object_cdexc
object_centroids
object_circ.
object_circex
object_compentropy
object_compm1
object_compm2
object_compm3
object_compmean
object_compslope
object_convarea
object_convarea_area
object_convperim
object_convperim_perim
object_cv
object_date
object_depth_max
object_depth_min
object_elongation
object_esd
object_fcons
object_feret
object_feretareaexc
object_fractal
object_height
object_histcum1
object_histcum2
object_histcum3
object_id
object_intden
object_kurt
object_kurt_mean
object_lat
object_link
object_lon
object_major
object_max
object_mean
object_meanimagegrey
object_meanpos
object_median
object_median_mean
object_median_mean_range
object_min
object_minor
object_mode
object_nb1
object_nb1_area
object_nb1_range
object_nb2
object_nb2_area
object_nb2_range
object_nb3
object_nb3_area
object_nb3_range
object_perim.
object_perimareaexc
object_perimferet
object_perimmajor
object_range
object_skelarea
object_skeleton_area
object_skew
object_skew_mean
object_slope
object_sr
object_stddev
object_symetrieh
object_symetrieh_area
object_symetriehc
object_symetriev
object_symetriev_area
object_symetrievc
object_tag
object_thickr
object_time
object_width
object_x
object_xm
object_xmg5
object_xstart
object_y
object_ym
object_ymg5
object_ystart
process_background_method
process_esd_max
process_esd_min
process_gamma_value
process_grey_auto_adjust
process_id
process_lut_offset
process_lut_slope
process_nb_images
process_nb_of_rawfile_images_in_folder
process_objects_processed
process_pixel
process_remove_duplicates
process_remove_objects_on_sides
process_rolling
process_scale
process_software
process_start_date
process_start_time
process_stop_after_m_objects
process_stop_n_images
process_upper
sample_barcode
sample_comment_or_volume
sample_dataportal_descriptor
sample_filename
sample_id
sample_project
sample_samplinggear
sample_ship
sample_volconc
sample_volpump


