=============
Remote access
=============

.. warning::

    Make sure your Raspberry Pi is connected to Internet either via WiFi or Ethernet.
 
Update your Pi
==============
    
Use the command lines to first update and upgrade your Raspbian ::

    $ sudo apt-get update -y
    $ sudo apt-get dist-upgrade -y
    
It's a good practice to reboot after that using ::

    $ sudo reboot now
    
Packages installation
=====================

Install the packages for the standalone WiFi ::

    $ sudo apt-get install dnsmasq hostapd -y

Install the packages for the standalone WiFi ::

    $ sudo apt-get install dnsmasq hostapd -y
    $ sudo apt-get install git -y
    $ git clone https://github.com/silvanmelchior/RPi_Cam_Web_Interface.git
    $ cd RPi_Cam_Web_Interface
    $ ./install.sh
    
#
#
#
#
#


Setting up a Raspberry Pi as an access point in a standalone network (NAT)
==========================================================================

The Raspberry Pi can be used as a wireless access point, running a standalone network. This can be done using the inbuilt wireless features of the Raspberry Pi 3 or Raspberry Pi Zero W, or by using a suitable USB wireless dongle that supports access points.

Note that this documentation was tested on a Raspberry Pi 3, and it is possible that some USB dongles may need slight changes to their settings. If you are having trouble with a USB wireless dongle, please check the forums.

To add a Raspberry Pi-based access point to an existing network, see this section.

In order to work as an access point, the Raspberry Pi will need to have access point software installed, along with DHCP server software to provide connecting devices with a network address.

To create an access point, we'll need DNSMasq and HostAPD. Install all the required software in one go with this command::

        sudo apt install dnsmasq hostapd
        
Since the configuration files are not ready yet, turn the new software off as follows::

        sudo systemctl stop dnsmasq
        sudo systemctl stop hostapd

Configuring a static IP
=======================

We are configuring a standalone network to act as a server, so the Raspberry Pi needs to have a static IP address assigned to the wireless port. This documentation assumes that we are using the standard 192.168.x.x IP addresses for our wireless network, so we will assign the server the IP address 192.168.4.1. It is also assumed that the wireless device being used is wlan0.

To configure the static IP address, edit the dhcpcd configuration file with::

        sudo touch /etc/dhcpcd.conf
        chmod 777 /etc/dhcpcd.conf

Send the desired IP address to the end of the previous generated .conf::

        echo "interface wlan0" >> /etc/dhcpcd.conf
        echo "	static ip_address=192.168.4.1/24" >> /etc/dhcpcd.conf
        echo "	nohook wpa_supplicant" >> /etc/dhcpcd.conf
    
Now restart the dhcpcd daemon and set up the new wlan0 configuration::

        sudo service dhcpcd restart

Configuring the DHCP server (dnsmasq)
=====================================

The DHCP service is provided by dnsmasq. By default, the configuration file contains a lot of information that is not needed, and it is easier to start from scratch. Rename this configuration file, and edit a new one:

        sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
        sudo touch /etc/dnsmasq.conf
        sudo chmod 777 /etc/dnsmasq.conf

Type or copy the following information into the dnsmasq configuration file and save it::

        sudo echo "interface=wlan0" >> /etc/dnsmasq.conf
        sudo echo "	dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h" >> /etc/dnsmasq.conf
        
So for wlan0, we are going to provide IP addresses between 192.168.4.2 and 192.168.4.20, with a lease time of 24 hours. If you are providing DHCP services for other network devices (e.g. eth0), you could add more sections with the appropriate interface header, with the range of addresses you intend to provide to that interface.

There are many more options for dnsmasq; see the dnsmasq `documentation`_  for more details.

.. _documentation: http://www.thekelleys.org.uk/dnsmasq/doc.html


Reload dnsmasq to use the updated configuration::

        sudo systemctl reload dnsmasq


        
