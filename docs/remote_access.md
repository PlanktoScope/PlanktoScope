# Remote access via a standalone network

## Setting up a Raspberry Pi as an access point in a standalone network (NAT)

This tutorial is adapted from an official Raspberry Pi tutorial that you can find [here](https://www.raspberrypi.org/documentation/configuration/wireless/access-point.md#internet-sharing).

In order to work as an access point, the Raspberry Pi will need to have access point software installed, along with DHCP server software to provide connecting devices with a network address.

To create an access point, we'll need DNSMasq and HostAPD. Install all the required software in one go with this command::
```
        sudo apt install dnsmasq hostapd
```

Since the configuration files are not ready yet, turn the new software off as follows::
```
        sudo systemctl stop dnsmasq
        sudo systemctl stop hostapd
```

### Configuring a static IP

We are configuring a standalone network to act as a server, so the Raspberry Pi needs to have a static IP address assigned to the wireless port. This documentation assumes that we are using the standard 192.168.x.x IP addresses for our wireless network, so we will assign the server the IP address 192.168.4.1. It is also assumed that the wireless device being used is wlan0.

To configure the static IP address, edit the dhcpcd configuration file with::
```
        sudo touch /etc/dhcpcd.conf
        chmod 777 /etc/dhcpcd.conf
```

Send the desired IP address to the end of the previous generated .conf::
```
        echo "interface wlan0" >> /etc/dhcpcd.conf
        echo "	static ip_address=192.168.4.1/24" >> /etc/dhcpcd.conf
        echo "	nohook wpa_supplicant" >> /etc/dhcpcd.conf
```

Now restart the dhcpcd daemon and set up the new wlan0 configuration::
```
        sudo service dhcpcd restart
```

### Configuring the DHCP server (dnsmasq)

The DHCP service is provided by dnsmasq. By default, the configuration file contains a lot of information that is not needed, and it is easier to start from scratch. Rename this configuration file, and edit a new one::
```
        sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
        sudo touch /etc/dnsmasq.conf
        sudo chmod 777 /etc/dnsmasq.conf
```

Type or copy the following information into the dnsmasq configuration file and save it::
```
        sudo echo "interface=wlan0" >> /etc/dnsmasq.conf
        sudo echo "	dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h" >> /etc/dnsmasq.conf
```

So for wlan0, we are going to provide IP addresses between 192.168.4.2 and 192.168.4.20, with a lease time of 24 hours. If you are providing DHCP services for other network devices (e.g. eth0), you could add more sections with the appropriate interface header, with the range of addresses you intend to provide to that interface.

There are many more options for dnsmasq; see the dnsmasq [documentation](http://www.thekelleys.org.uk/dnsmasq/doc.html) for more details.


Reload dnsmasq to use the updated configuration::
```
        sudo systemctl reload dnsmasq
```

### Configuring the access point host software (hostapd)

You need to edit the hostapd configuration file, located at /etc/hostapd/hostapd.conf, to add the various parameters for your wireless network. After initial install, this will be a new/empty file. ::
```        
        sudo touch /etc/hostapd/hostapd.conf
        sudo chmod 777 /etc/hostapd/hostapd.conf
```

Add the information below to the configuration file. This configuration assumes we are using channel 7, with a network name of NameOfNetwork, and a password AardvarkBadgerHedgehog. Note that the name and password should not have quotes around them. The passphrase should be between 8 and 64 characters in length.

To use the 5 GHz band, you can change the operations mode from hw_mode=g to hw_mode=a. Possible values for hw_mode are:

- `a` = IEEE 802.11a (5 GHz)
- `b` = IEEE 802.11b (2.4 GHz)
- `g` = IEEE 802.11g (2.4 GHz)
- `ad` = IEEE 802.11ad (60 GHz) (Not available on the Raspberry Pi)

WARNING: Make sure you **define the wished name (ssid)** of the futur generated Wifi and its **password (wpa_passphrase)**.

Set up your hoastapd.conf as follow ::
```
        sudo echo "interface=wlan0" >> /etc/hostapd/hostapd.conf
        sudo echo "driver=nl80211" >> /etc/hostapd/hostapd.conf
        sudo echo "ssid=NameOfNetwork" >> /etc/hostapd/hostapd.conf
        sudo echo "hw_mode=g" >> /etc/hostapd/hostapd.conf
        sudo echo "channel=7" >> /etc/hostapd/hostapd.conf
        sudo echo "wmm_enabled=0" >> /etc/hostapd/hostapd.conf
        sudo echo "macaddr_acl=0" >> /etc/hostapd/hostapd.conf
        sudo echo "auth_algs=1" >> /etc/hostapd/hostapd.conf
        sudo echo "ignore_broadcast_ssid=0" >> /etc/hostapd/hostapd.conf
        sudo echo "wpa=2" >> /etc/hostapd/hostapd.conf
        sudo echo "wpa_passphrase=YourPassword" >> /etc/hostapd/hostapd.conf
        sudo echo "wpa_key_mgmt=WPA-PSK" >> /etc/hostapd/hostapd.conf
        sudo echo "wpa_pairwise=TKIP" >> /etc/hostapd/hostapd.conf
        sudo echo "rsn_pairwise=CCMP" >> /etc/hostapd/hostapd.conf
```

We now need to tell the system where to find this configuration file.
```
        sudo chmod 777 /etc/default/hostapd
```

Find the line with #DAEMON_CONF, and replace it with this
```     
        sudo echo 'DAEMON_CONF="/etc/hostapd/hostapd.conf"' >> /etc/default/hostapd
```

### Start it up

Now enable and start hostapd
```
        sudo systemctl unmask hostapd
        sudo systemctl enable hostapd
        sudo systemctl start hostapd
```

Do a quick check of their status to ensure they are active and running
```
        sudo systemctl status hostapd
        sudo systemctl status dnsmasq
```

Add routing and masquerade

Edit /etc/sysctl.conf and uncomment a line
```
        VAR=$(sudo grep -n -m 1 net.ipv4.ip_forward=1 /etc/sysctl.conf | sudo sed  's/\([0-9]*\).*/\1/')
        sudo sed -i "${VAR}s/# *//" /etc/sysctl.conf
```

Add a masquerade for outbound traffic on eth0
```
        sudo iptables -t nat -A  POSTROUTING -o eth0 -j MASQUERADE
```

Save the iptables rule
```
        sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"
```

Edit /etc/rc.local and add this just above "exit 0" to install these rules on boot
```
        sudo chmod 777 /etc/rc.local
        sudo sed -i  '/exit 0/d' /etc/rc.local
        sudo echo "iptables-restore < /etc/iptables.ipv4.nat" >> /etc/rc.local
        sudo echo "exit 0" >> /etc/rc.local
```

Reboot and ensure it still functions.

Using a wireless device, search for networks. The network SSID you specified in the hostapd configuration should now be present, and it should be accessible with the specified password.

If SSH is enabled on the Raspberry Pi access point, it should be possible to connect to it from another Linux box (or a system with SSH connectivity present) as follows, assuming the pi account is present
```
        ssh pi@192.168.4.1
```
Most likely your password will be **raspberry**.

By this point, the Raspberry Pi is acting as an access point, and other devices can associate with it. Associated devices can access the Raspberry Pi access point via its IP address for operations such as rsync, scp, or ssh.
