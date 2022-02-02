# Remote access via a standalone network

This tutorial is adapted from a tutorial that you can find [here](https://www.raspberryconnect.com/projects/65-raspberrypi-hotspot-accesspoints/157-raspberry-pi-auto-wifi-hotspot-switch-internet).

All the files modified in this document are also available in the repository, in the folder `scripts/raspbian_configuration`. The architecture of this folder shows where each file belong.

In order to work as an access point, the Raspberry Pi will need to have access point software installed, along with DHCP server software to provide connecting devices with a network address.

To create an access point, we'll need DNSMasq and HostAPD. Install all the required software in one go with this command::
```sh
sudo apt install dnsmasq hostapd
```

Since the configuration files are not ready yet, turn the new software off as follows::
```sh
sudo systemctl unmask hostapd
sudo systemctl disable dnsmasq
sudo systemctl disable hostapd
```

## Configuring HostAPD

Using a text editor edit the hostapd configuration file. This file won't exist at this stage so will be blank: `sudo nano /etc/hostapd/hostapd.conf`

```
#2.4GHz setup wifi 80211 b,g,n
interface=wlan0
driver=nl80211
ssid=PlanktoScope-Bababui_Tuogaore
hw_mode=g
channel=8
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=copepode
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP TKIP
rsn_pairwise=CCMP

#80211n - Change GB to your WiFi country code
country_code=FR
ieee80211n=1
ieee80211d=1
```

The interface will be wlan0. The driver nl80211 works with the Raspberry RPi 4, RPi 3B+, RPi 3 & Pi Zero W onboard WiFi but you will need to check that your wifi dongle is compatable and can use Access Point mode.

For more information on wifi dongles see elinux.org/RPi_USB_Wi-Fi_Adapters

The SSID is the name of the WiFi signal broadcast from the RPi, which you will connect to with your Tablet or phones WiFi settings.
Channel can be set between 1 and 13. If you are having trouble connection because of to many wifi signals in your area are using channel 8 then try another channel.
Wpa_passphrase is the password you will need to enter when you first connect a device to your Raspberry Pi's hotspot. This should be at least 8 characters and a bit more difficult to guess than my example.
The country_code should be set to your country to comply with local RF laws. You may experience connection issues if this is not correct. Your country_code can be found in /etc/wpa_supplicant/wpa_supplicant.conf or in Raspberry Pi Configuration - Localisation settings

To save the config file press `CTRL+O` and to exit press `CTRL+X`.

We also use a special function to change the network name to the machine name. Add this to `/etc/rc.local` with `sudo nano /etc/rc.local`:
```sh
# Replace wifi hostname
sed -i "s/^ssid.*/ssid=PlanktoScope-$(python3 -c "import planktoscope.uuidName as uuidName; print(uuidName.machineName(machine=uuidName.getSerial()).replace(' ','_'))")/" /etc/hostapd/hostapd.conf
```

Now the defaults file needs to be updated to point to where the config file is stored.
In terminal enter the command `sudo nano /etc/default/hostapd`

Change `#DAEMON_CONF=""` to `DAEMON_CONF="/etc/hostapd/hostapd.conf"`

Check the `DAEMON_OPTS=""` is preceded by a #, so is `#DAEMON_OPTS=""`.

And save.

## DNSmasq configuration

Next dnsmasq needs to be configured to allow the Rpi to act as a router and issue ip addresses. Open the dnsmasq.conf file with `sudo nano /etc/dnsmasq.conf`

Go to the bottom of the file and add the following lines:
```
#AutoHotspot config
interface=wlan0
bind-dynamic 
server=1.1.1.1
domain-needed
bogus-priv
dhcp-range=192.168.4.100,192.168.4.200,12h

#AutoEthernet config
interface=eth0
bind-dynamic
server=1.1.1.1
domain-needed
bogus-priv
dhcp-range=192.168.5.100,192.168.5.200,12h
```

and then save `CTRL+O` and exit `CTRL+X`.

Reload dnsmasq to use the updated configuration:
```sh
sudo systemctl reload dnsmasq
```

## DHCPCD

DHCPCD is the software that manages the network setup. The next step is to stop dhcpcd from starting the wifi network so the autohotspot script in the next step takes control of that. Ethernet will still be managed by dhcpcd.

This will also create a fallback configuration to a static IP if no DHCP server is present on the Ethernet network.

Just add this line to the end of /etc/dhcpcd.conf with `sudo nano /etc/dhcpcd.conf`:
```
nohook wpa_supplicant

# define static profile
profile static_eth0
static ip_address=192.168.5.1/24
static routers=192.168.5.1
static domain_name_servers=192.168.5.1

# fallback to static profile on eth0
interface eth0
fallback static_eth0
```
Save and exit.

For the fallback Ethernet network to work, we also need to add a hook to DHCPCD so it starts up the local DHCP server (dnsmasq). Edit the file `/etc/dhcpcd.enter-hook` with `sudo nano /etc/dhcpcd.enter-hook`:

```sh
if [ "$interface" = "eth0" ] && [ "$if_up" ]; then
  systemctl start dnsmasq
  if [ "$reason" = "STATIC" ] || [ "$reason" = "TIMEOUT" ] || [ "$reason" = "EXPIRE" ] || [ "$reason" = "NAK" ]; then
    systemctl start dnsmasq
  elif [ "$reason" = "NOCARRIER" ] || [ "$reason" = "INFORM" ] || [ "$reason" = "DEPARTED" ]; then
    systemctl stop dnsmasq
  fi
fi
```


## Autohotspot service file

Next we have to create a service which will run the autohotspot script when the Raspberry Pi starts up.
Create a new file with the command `sudo nano /etc/systemd/system/autohotspot.service`

Then enter the following text:
```
[Unit]
Description=Automatically generates a Hotspot when a valid SSID is not in range
After=multi-user.target
[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/autohotspotN
[Install]
WantedBy=multi-user.target
```

Save and exit.

For the service to work it has to be enabled. To do this enter the command `sudo systemctl enable autohotspot.service`.

## Service Timer

Create the timer with `sudo nano /etc/systemd/system/autohotspot.timer`:
```
# /etc/systemd/system/autohotspot.timer
[Unit]
Description=Run autohotspot every 5 minutes, starting 10 seconds after system boot

[Timer]
OnBootSec=5sec
OnUnitActivateSec=5min 

[Install]
WantedBy=timers.target
```
Save and exit.

Activate with `sudo systemctl enable autohotspot.timer`.

### AutoHotspot Script

This is the main script that will manage your wifi connections between a wifi router and an Access Point.

It will search for any wifi connection that is setup on you Raspberry Pi by using the details found in /etc/wpa_supplicant/wpa_supplicant.conf

If no wifi signal is found for a known SSID then the script will shutdown the wifi network setup and create a Hotspot. If an ethernet cable that allows internet access is connect then the Hotspot will become a full internet access point. Allowing all connected devices to use the Internet. Without an ethernet connect the Raspberry Pi can be accessed from a wifi device using SSH or VNC.

The script works with SSID's that contain spaces and by entering your routers MAC address it can be used with hidden SSID's.
!!! info
    Hidden SSIDs

    If your routers SSID is not broadcast/hidden then find this section in the script

    ```
    #Enter the Routers Mac Addresses for hidden SSIDs, seperated by spaces ie
    #( '11:22:33:44:55:66' 'aa:bb:cc:dd:ee:ff' )
    mac=()
    ```

    and enter you routers MAC address in the brackets of mac=() as shown in the example. Make sure mutiple MAC addresses are seperated by a space.

Create a new file with the command `sudo nano /usr/bin/autohotspotN` and add the following:
```sh
#!/bin/bash
#version 0.961-N/HS-I-PlanktonPlanet

#changes by PlanktonPlanet includes the following:
#- formatting and shellcheck validation
#- removal of ip forwarding setup

#You may share this script on the condition a reference to RaspberryConnect.com
#must be included in copies or derivatives of this script.

#Network Wifi & Hotspot with Internet
#A script to switch between a wifi network and an Internet routed Hotspot
#A Raspberry Pi with a network port required for Internet in hotspot mode.
#Works at startup or with a seperate timer or manually without a reboot
#Other setup required find out more at
#http://www.raspberryconnect.com

wifidev="wlan0" #device name to use. Default is wlan0.
ethdev="eth0"   #Ethernet port to use with IP tables
#use the command: iw dev ,to see wifi interface name

#These two lines capture the wifi networks the RPi is setup to use
wpassid=$(awk '/ssid="/{ print $0 }' /etc/wpa_supplicant/wpa_supplicant.conf | awk -F'ssid=' '{ print $2 }' | sed 's/\r//g' | awk 'BEGIN{ORS=","} {print}' | sed 's/\"/''/g' | sed 's/,$//')
IFS="," read -r -a ssids <<<"$wpassid"

#Note:If you only want to check for certain SSIDs
#Remove the # in in front of ssids=('mySSID1'.... below and put a # infront of all four lines above
# separated by a space, eg ('mySSID1' 'mySSID2')
#ssids=('mySSID1' 'mySSID2' 'mySSID3')

#Enter the Routers Mac Addresses for hidden SSIDs, seperated by spaces ie
#( '11:22:33:44:55:66' 'aa:bb:cc:dd:ee:ff' )
mac=()

ssidsmac=("${ssids[@]}" "${mac[@]}") #combines ssid and MAC for checking

createAdHocNetwork() {
       echo "Creating Hotspot"
       ip link set dev "$wifidev" down
       ip a add 192.168.4.1/24 brd + dev "$wifidev"
       ip link set dev "$wifidev" up
       dhcpcd -k "$wifidev" >/dev/null 2>&1
       systemctl start dnsmasq
       systemctl start hostapd
}

KillHotspot() {
       echo "Shutting Down Hotspot"
       ip link set dev "$wifidev" down
       systemctl stop hostapd
       systemctl stop dnsmasq
       ip addr flush dev "$wifidev"
       ip link set dev "$wifidev" up
       dhcpcd -n "$wifidev" >/dev/null 2>&1
}

ChkWifiUp() {
       echo "Checking WiFi connection ok"
       sleep 20                                                                    #give time for connection to be completed to router
       if ! wpa_cli -i "$wifidev" status | grep 'ip_address' >/dev/null 2>&1; then #Failed to connect to wifi (check your wifi settings, password etc)
              echo 'Wifi failed to connect, falling back to Hotspot.'
              wpa_cli terminate "$wifidev" >/dev/null 2>&1
              createAdHocNetwork
       fi
}

chksys() {
       #After some system updates hostapd gets masked using Raspbian Buster, and above. This checks and fixes
       #the issue and also checks dnsmasq is ok so the hotspot can be generated.
       #Check Hostapd is unmasked and disabled
       if systemctl -all list-unit-files hostapd.service | grep "hostapd.service masked" >/dev/null 2>&1; then
              systemctl unmask hostapd.service >/dev/null 2>&1
       fi
       if systemctl -all list-unit-files hostapd.service | grep "hostapd.service enabled" >/dev/null 2>&1; then
              systemctl disable hostapd.service >/dev/null 2>&1
              systemctl stop hostapd >/dev/null 2>&1
       fi
       #Check dnsmasq is disabled
       if systemctl -all list-unit-files dnsmasq.service | grep "dnsmasq.service masked" >/dev/null 2>&1; then
              systemctl unmask dnsmasq >/dev/null 2>&1
       fi
       if systemctl -all list-unit-files dnsmasq.service | grep "dnsmasq.service enabled" >/dev/null 2>&1; then
              systemctl disable dnsmasq >/dev/null 2>&1
              systemctl stop dnsmasq >/dev/null 2>&1
       fi
}

FindSSID() {
       #Check to see what SSID's and MAC addresses are in range
       ssidChk='NoSSid'
       i=0
       j=0
       until [ $i -eq 1 ]; do #wait for wifi if busy, usb wifi is slower.
              ssidreply=$( (iw dev "$wifidev" scan ap-force | grep -E "^BSS|SSID:") 2>&1) >/dev/null 2>&1
              #echo "SSid's in range: " $ssidreply
              printf '%s\n' "${ssidreply[@]}"
              echo "Device Available Check try " $j
              if ((j >= 5)); then #if busy 5 times goto hotspot
                     echo "Device busy or unavailable 5 times, going to Hotspot"
                     ssidreply=""
                     i=1
              elif echo "$ssidreply" | grep "No such device (-19)" >/dev/null 2>&1; then
                     echo "No Device Reported, try " $j
                     NoDevice
              elif echo "$ssidreply" | grep "Network is down (-100)" >/dev/null 2>&1; then
                     echo "Network Not available, trying again" $j
                     j=$((j + 1))
                     sleep 2
              elif echo "$ssidreply" | grep "Read-only file system (-30)" >/dev/null 2>&1; then
                     echo "Temporary Read only file system, trying again"
                     j=$((j + 1))
                     sleep 2
              elif echo "$ssidreply" | grep "Invalid exchange (-52)" >/dev/null 2>&1; then
                     echo "Temporary unavailable, trying again"
                     j=$((j + 1))
                     sleep 2
              elif echo "$ssidreply" | grep -v "resource busy (-16)" >/dev/null 2>&1; then
                     echo "Device Available, checking SSid Results"
                     i=1
              else #see if device not busy in 2 seconds
                     echo "Device unavailable checking again, try " $j
                     j=$((j + 1))
                     sleep 2
              fi
       done

       for ssid in "${ssidsmac[@]}"; do
              if (echo "$ssidreply" | grep -F -- "$ssid") >/dev/null 2>&1; then
                     #Valid SSid found, passing to script
                     echo "Valid SSID Detected, assesing Wifi status"
                     ssidChk=$ssid
                     return 0
              else
                     #No Network found, NoSSid issued"
                     echo "No SSid found, assessing WiFi status"
                     ssidChk='NoSSid'
              fi
       done
}

NoDevice() {
       #if no wifi device,ie usb wifi removed, activate wifi so when it is
       #reconnected wifi to a router will be available
       echo "No wifi device connected"
       wpa_supplicant -B -i "$wifidev" -c /etc/wpa_supplicant/wpa_supplicant.conf >/dev/null 2>&1
       exit 1
}

chksys
FindSSID

#Create Hotspot or connect to valid wifi networks
if [ "$ssidChk" != "NoSSid" ]; then
       if systemctl status hostapd | grep "(running)" >/dev/null 2>&1; then #hotspot running and ssid in range
              KillHotspot
              echo "Hotspot Deactivated, Bringing Wifi Up"
              wpa_supplicant -B -i "$wifidev" -c /etc/wpa_supplicant/wpa_supplicant.conf >/dev/null 2>&1
              ChkWifiUp
       elif { wpa_cli -i "$wifidev" status | grep 'ip_address'; } >/dev/null 2>&1; then #Already connected
              echo "Wifi already connected to a network"
       else #ssid exists and no hotspot running connect to wifi network
              echo "Connecting to the WiFi Network"
              wpa_supplicant -B -i "$wifidev" -c /etc/wpa_supplicant/wpa_supplicant.conf >/dev/null 2>&1
              ChkWifiUp
       fi
else #ssid or MAC address not in range
       if systemctl status hostapd | grep "(running)" >/dev/null 2>&1; then
              echo "Hostspot already active"
       elif { wpa_cli status | grep "$wifidev"; } >/dev/null 2>&1; then
              echo "Cleaning wifi files and Activating Hotspot"
              wpa_cli terminate >/dev/null 2>&1
              ip addr flush "$wifidev"
              ip link set dev "$wifidev" down
              # ip addr flush "$ethdev"
              # ip link set dev "$ethdev" down
              rm -r /var/run/wpa_supplicant >/dev/null 2>&1
              createAdHocNetwork
       else #"No SSID, activating Hotspot"
              createAdHocNetwork
       fi
fi

```

Save and exit.

Make this script executable with `sudo chmod +x /usr/bin/autohotspotN`.

You can now reboot your machine. If it doesn't find the a setup wifi network, it will generate its own.