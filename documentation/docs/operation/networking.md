# Networking guide

By default, your PlanktoScope creates an [isolated Wi-Fi network](./index.md#connect-with-the-planktoscopes-isolated-wi-fi-network) (which we often call "the PlanktoScope's Wi-Fi hotspot network") which devices can connect to in order to access the PlanktoScope's software; and devices can also connect to the PlanktoScope directly [by an Ethernet cable](./index.md#connect-with-an-ethernet-cable). However, you may have reasons to adjust your networking configuration away from this default. This guide provides instructions on how to adjust your networking configuration in various ways.

Currently, all instructions in this guide should be considered as being provided for "advanced users" (and/or for users who are able to ask for help in the PlanktoScope Slack workspace). These instructions will probably change between between successive releases of the PlanktoScope software. All URLs in this guide are written assuming you access your PlanktoScope using [planktoscope.local](http://planktoscope.local) as the domain name; if you need to use [some other domain name](./index.md#access-your-planktoscopes-software) such as [home.pkscope](http://home.pkscope), you should replace `planktoscope.local` with that other domain name in all the links on this page.

## Adjust your PlanktoScope's Wi-Fi region settings

By default, the PlanktoScope's Wi-Fi settings are configured in compliance with United States Wi-Fi [regulatory domain](https://en.wikipedia.org/wiki/IEEE_802.11#Regulatory_domains_and_legal_compliance). If you're operating your PlanktoScope in another country, we recommend changing the Wi-Fi settings to match your country, which you can do by editing the file at `/etc/default/crda`. For example, you can do this in the file browser at <http://planktoscope.local/admin/fs/files/etc/default/crda>. You should replace the string `US` with a [ISO/IEC 3166-1 alpha-2 country code](https://en.wikipedia.org/wiki/ISO_3166-1#Codes) corresponding to your country. To apply your changes, restart the PlanktoScope.

To revert your changes back to the US regulatory domain, we recommend deleting the file at `/var/lib/overlays/overrides/etc/default/crda`. For example, you can do this in the file browser at <http://planktoscope.local/admin/fs/files/var/lib/overlays/overrides/etc/default/> . Then restart the PlanktoScope immediately.

### Change Wi-Fi hotspot region settings

By default, the PlanktoScope makes its Wi-Fi hotspot network on [WLAN channel](https://en.wikipedia.org/wiki/List_of_WLAN_channels) 8 in the 2.4 GHz range (802.11b/g), which should generally be compatible with regulations across all countries. However, if your computer/phone/etc.'s connection to the PlanktoScope's Wi-Fi hotspot is unstable and/or you are operating your PlanktoScope outside the United States, you might need to change your Wi-Fi hotspot's regional settings.

To change the regional settings of the PlanktoScope's Wi-Fi hotspot away from the defaults, edit the file at `/etc/NetworkManager/system-connections.d/wlan0-hotspot/31-wifi-regional.nmconnection`. For example, you can do this by opening the file editor at <http://planktoscope.local/admin/fs/files/etc/NetworkManager/system-connections.d/wlan0-hotspot/31-wifi-regional.nmconnection> . To apply your changes, restart the PlanktoScope.

To revert your changes back to the default regional settings, we recommend deleting the file at `/var/lib/overlays/overrides/etc/NetworkManager/system-connections.d/wlan0-hotspot/31-wifi-regional.nmconnection`. For example, you can do this in the file browser at <http://planktoscope.local/admin/fs/files/var/lib/overlays/overrides/etc/NetworkManager/system-connections.d/wlan0-hotspot/> . Then restart the PlanktoScope immediately.

Note that the above instructions are given for the Wi-Fi hotspot generated from the internal Wi-Fi module in your PlanktoScope's Raspberry Pi computer, which is named `wlan0`. If you want to change the regional settings for a Wi-Fi hotspot generated from a USB Wi-Fi dongle plugged into the Raspberry Pi, which will be named `wlan1`, then you should replace `wlan0` with `wlan1` in the above links/filenames.

## Connect your PlanktoScope to the internet

To connect your PlanktoScope to the internet, we recommend one of the following options:

1. Plug it into an Ethernet port with internet access.
2. Connect an Android phone/tablet by USB to your PlanktoScope and then enabling USB tethering mode so that the Android device shares its internet access (which can be from the Wi-Fi network it's connected to) to the PlanktoScope. Note: we plan to add support for USB tethering from iOS devices, but we haven't figured out how to do that yet.
3. Plug a USB Wi-Fi dongle into your PlanktoScope and then connect to a Wi-Fi network using it, while maintaining a Wi-Fi hotspot from the internal Wi-Fi module in your PlanktoScope's Raspberry Pi computer.
4. Plug a USB Wi-Fi dongle into your PlanktoScope to generate a Wi-Fi hotspot from it, and then connect to a Wi-Fi network using the internal Wi-Fi module in your PlanktoScope's Raspberry Pi computer.

Once your PlanktoScope is connected to the internet, by default it will attempt to share its internet access with any devices connected to the PlanktoScope by Wi-Fi hotspot or by Ethernet.

If you need to connect to a network which requires you to register your PlanktoScope's MAC address (also known as the "hardware address" of your PlanktoScope's network adapter(s)), please refer to [a subsection below](#check-your-planktoscopes-mac-addresses).

### Connect your PlanktoScope to an existing Wi-Fi network with a second Wi-Fi module

First, you should plug in your USB Wi-Fi dongle. It needs to have Linux driver support to work; information about compatible USB Wi-FI dongles which are reasonably compact can be found [here](https://github.com/morrownr/USB-WiFi/blob/main/home/USB_WiFi_Adapters_that_are_supported_with_Linux_in-kernel_drivers.md#single-band-usb-wifi-adapters-that-are-supported-with-linux-in-kernel-drivers); we have had good results with the [Panda PAU03 N150 adapter](https://www.amazon.com/Panda-Ultra-150Mbps-Wireless-Adapter/dp/B00762YNMG). If the Wi-Fi dongle works, then by default your PlanktoScope should create a Wi-Fi hotspot on it; you can check this by running the command `sudo nmcli conn` in the Cockpit Terminal at <http://planktoscope.local/admin/cockpit/system/terminal> (which you should log in to with the username `pi` and the `pi` user's password, which is `copepode` by default) and checking whether the `wlan1-hotspot` connection is active (i.e. listed in bright green rather than white). If the Wi-Fi dongle works, then you can create a new Wi-Fi connection for it.

To create a new Wi-Fi connection, run the command `sudo nmtui edit` and follow the dialogs to add a new Wi-Fi connection. In the "Edit Connection" window, you should specify either `wlan0` or `wlan1` as the device for that connection, depending on whether you want to connect to that Wi-Fi network with your Raspberry Pi's internal Wi-Fi module (`wlan0`) or with your USB Wi-Fi dongle (`wlan1`); then you should avoid creating any Wi-Fi connections for the other Wi-Fi module, so that it will still make a Wi-Fi hotspot. Then you can activate that new connection by rebooting or by running the command `sudo nmcli conn up "{connection name}"`, where `{connection name}` should be replaced with the connection profile name you had set when you created that connection. For example, if you created a Wi-Fi connection named `My Favorite Connection`, then you would run `sudo nmcli conn up "My Favorite Connection"`. It will take a while to finish, after which either the connection will have activated successfully or the command will have printed an error message. You can run `sudo nmtui conn` again to check what connections are active on your PlanktoScope.

Once your PlanktoScope is connected to that external Wi-Fi network, you should try to access it through that network via your PlanktoScope's machine-specific mDNS URL, which has format `http://pkscope-{machine-name}.local`; in order to test whether this works, you will need to disconnect any direct connections your computer might have to your PlanktoScope (e.g. via a Wi-Fi hotspot on the other Wi-Fi module, or via a direct Ethernet connection). Note that your PlanktoScope might not be reachable over the external Wi-Fi network if your Wi-Fi network has restrictive firewall settings, in which case you will only be able to connect to your PlanktoScope directly via Ethernet cable. Note also that this URL only works if your device and web browser both support mDNS.

You may also want to check whether you can access the internet on the PlanktoScope. If the Wi-Fi network has a captive portal (e.g. for device registration or for a terms-of-service agreement), you should disconnect your computer from any Wi-Fi/Ethernet networks with internet access (in order to force it to use the PlanktoScope for internet access) and then try to open a webpage (e.g. <http://google.com>) in your computer's web browser to see if you can access the captive portal. If the Wi-Fi network doesn't have a captive portal, or if you successfully proceed through the captive portal, then you should be able to load web-pages using the internet access shared by the PlanktoScope.

As long as the configuration exists for this Wi-Fi connection, your PlanktoScope will then prefer to use the specified Wi-Fi module to connect to that Wi-Fi network if it's in range during startup; this will remain true even if you reboot your PlanktoScope. If the PlanktoScope loses its connection to the Wi-Fi network (e.g. because it is moved out of the range of that network), then it will automatically revert back to making its Wi-Fi hotspot using that Wi-Fi module, until the next reboot. If you want to revert back to always making a Wi-Fi hotspot from that Wi-Fi module, then you can run the command `sudo nmtui edit` and delete that Wi-Fi connection.

### Connect your PlanktoScope to an existing Wi-Fi network with a single Wi-Fi module

It's also possible to connect a PlanktoScope with a single Wi-Fi module to an existing Wi-Fi network with internet access (using the same instructions as given above, but specifying `wlan0` as the device for your Wi-Fi connection and skipping the steps related to plugging in a USB Wi-Fi dongle), but the PlanktoScope will be unable to make its Wi-Fi hotspot network while it is connected to an existing Wi-Fi network. Then, as long as the PlanktoScope boots up and stays within range of that Wi-Fi network, the PlanktoScope software is only accessible either if 1) the existing Wi-Fi network (including its firewall settings) is configured to allow you to access the PlanktoScope via mDNS and your computer and web browser both support mDNS URLs (i.e. URLs ending in `.local`, like <http://planktoscope.local>) or if 2) you connect your device to the PlanktoScope via an Ethernet cable.

Once you take the PlanktoScope out of range of the existing Wi-Fi network, it should automatically revert to making its own Wi-Fi hotspot network. If you then take the PlanktoScope back in range of the existing Wi-Fi network, nothing will change until you either restart or manually switch back to the existing Wi-Fi network.

!!! warning

    Because you can only undo this configuration change by accessing the PlanktoScope's software (or by running a Linux computer which can open and edit the configuration files in `/var/lib/overlays/overrides/etc/NetworkManager/system-connections/` for Wi-Fi network connections in your PlanktoScope's SD card), we only recommend configuring a PlanktoScope with a single Wi-Fi module to connect to an existing Wi-Fi network if 1) you also have a way to connect your device to the PlanktoScope via an Ethernet cable or if 2) you are also able to run your PlanktoScope in a location beyond the range of the existing Wi-Fi network (as that the PlanktoScope will revert to making a Wi-Fi hotspot when it cannot detect the existing Wi-Fi network) or if 3) you have a Linux computer which is able to edit files on your PlanktoScope's SD card.

!!! warning

    Before you make any changes, you should first write down your PlanktoScope's machine name (which is listed in your PlanktoScope's landing page), and you should also check whether your web browser allows you to use the machine-specific URL of format `http://pkscope-{machine-name}.local` for accessing your PlanktoScope's landing page. This is because other URLs from our [standard software setup guide](../setup/software/standard-install.md#connect-to-the-planktoscope) and our [basic operation guide](./index.md#access-your-planktoscopes-software) which you may be more familiar with, such as <http://home.pkscope> or <http://192.168.4.1>, will not work for accessing your PlanktoScope through the existing Wi-Fi network! Only a URL like <http://planktoscope.local> or <http://pkscope.local> or a machine-specific URL of format `http://pkscope-{machine-name}.local` has the possibility of working.

FIXME: update this for NetworkManager with `sudo nmtui`. Does Cockpit make it easy to do this?

Once your PlanktoScope is connected to an existing Wi-Fi network, you should try to access it via your PlanktoScope's machine-specific mDNS URL, which has format `http://pkscope-{machine-name}.local`. Note that this may fail if your Wi-Fi network has restrictive firewall settings, in which case you will only be able to connect to your PlanktoScope directly via Ethernet cable. Note also that this URL only works if your device and web browser both support mDNS.

### Check your PlanktoScope's MAC addresses

If you need to check the MAC addresses (also sometimes called "hardware addresses") of your PlanktoScope's network interfaces (e.g. in order to register those network interfaces with a network firewall), you can open an auto-generated report of MAC addresses at `/run/mac-address.yml`, for example by opening the file viewer at <http://planktoscope.local/admin/fs/files/run/mac-addresses.yml>. That file viewer is also linked to from your PlanktoScope's landing page, in a link named "MAC address viewer" in the "For advanced users" section of the landing page. Note that this is a temporary file which only exists while the PlanktoScope is running - it is not stored on the PlanktoScope's SD card.

Usually you will only care about the MAC addresses for `wlan0` or `eth0`, which are the built-in Wi-Fi module and Ethernet port of the PlanktoScope's embedded Raspberry Pi computer, respectively. If you connect additional network adapters (such as a USB Wi-Fi dongle, an Ethernet-to-USB adapter, or a phone in USB tethering mode), then you may also see additional network interfaces named something like `wlan1`, `eth1`, or `usb0` around two minutes later.

Every two minutes, your PlanktoScope will refresh the list of MAC addresses, in case you connect any new network adapters to your PlanktoScope or disconnect any network adapters.

## Connect your client device to the internet while your PlanktoScope is not connected to the internet

If you can connect your PlanktoScope to the internet, then it will behave like a network router, sharing its internet access with all devices connected to the PlanktoScope; that's the easiest way to have your computer/phone/etc. connected to the PlanktoScope while still being able to access the internet. However, it is often useful to connect a computer simultaneously both to the internet and to a PlanktoScope which does not have internet access. You can do this through any of the following possible approaches:

1. Have your computer connect to the internet by an existing Wi-Fi network, and then connect your computer by Ethernet cable to the PlanktoScope.
2. Have your computer connect to the internet by an Ethernet cable, and then connect your computer to the PlanktoScope's Wi-Fi hotspot.
3. Connect a phone/tablet by USB to your computer and enable your phone/tablet's USB tethering mode to share its internet access to your computer, and then connect your computer to the PlanktoScope's Wi-Fi hotspot or to an Ethernet cable plugged into the PlanktoScope.
4. Add one or two USB Wi-Fi dongles to your computer so that it has a total of two Wi-Fi adapters (one of which may be internal to your computer) and thus can connect to two Wi-Fi networks simultaneously; then configure your computer to connect to the internet by an existing Wi-Fi network using one of the Wi-Fi adapters and to simultaneously connect to the PlanktoScope's Wi-Fi hotspot using the other Wi-Fi adapter.
5. Add one or two USB Ethernet adapters to your computer so that it has a total of two Ethernet adapters (one of which may be internal to your computer) and thus can connect to two Ethernet ports simultaneously; then connect one of your computer's Ethernet adapters to an Ethernet port with internet access, and connect your computer's other Ethernet adapter to the PlanktoScope.
6. Connect both your computer and the PlanktoScope to an [Ethernet switch](https://en.wikipedia.org/wiki/Network_switch), then connect your computer to the internet by an existing Wi-Fi network. Note 1: an Ethernet switch is a different kind of device than an Ethernet router. Note 2: if you then connect your Ethernet switch to an Ethernet or Wi-Fi router, then the PlanktoScope will only be accessible if the router's firewall allows network connections to the PlanktoScope from other devices on the router's Local Area Network (LAN).

### Don't allow the PlanktoScope to be used as a default gateway to the internet

Because by default your PlanktoScope is configured to act as a router so that it can share its internet access with all connected devices, it will advertise itself as a default gateway to the internet, so that connected devices will use the PlanktoScope as a network router for internet access. However, some computers (e.g. those running macOS or Windows) may behave as if the PlanktoScope is the *only* router with internet access even if the PlanktoScope actually has no internet access while the computer is also connected to a router for another network which *does* have internet access; then such computers will fail to access the internet while they're connected to the PlanktoScope.

You can work around this unfortunate behavior of your computer's operating system by disabling one or two settings in the PlanktoScope's networking configuration so that the PlanktoScope no longer advertises itself as a router with internet access; note that doing so will prevent the PlanktoScope from being able to share its own internet access with connected devices as long as these settings are disabled.

There are two settings, one controlling the behavior for Ethernet connections to the PlanktoScope and one controlling the behavior for the PlanktoScope's Wi-Fi hotspot. You can change just one setting, or you can change both settings together (in which case you can run both of the `forklift pallet disable-deployment-feature`/`forklift pallet enable-deployment-feature` commands consecutively and then just run the `forklift pallet stage --no-cache-img` command afterwards).

#### For Ethernet connections

To disable this setting for Ethernet connections to the PlanktoScope, run the following commands in the Cockpit Terminal at <http://planktoscope.local/admin/cockpit/system/terminal> (which you should log in to with the username `pi` and the `pi` user's password, which is `copepode` by default) and then restart the PlanktoScope:

```
forklift pallet disable-deployment-feature host/networking/networkmanager-dnsmasq dhcp-default-route
forklift pallet stage --no-cache-img
```

To revert this setting back to the default behavior (which is for the PlanktoScope to advertise itself as a router with internet access, so that the PlanktoScope can share its internet access with all connected devices), run the following commands in the Cockpit Terminal and then restart the PlanktoScope:

```
forklift pallet enable-deployment-feature host/networking/networkmanager-dnsmasq dhcp-default-route
forklift pallet stage --no-cache-img
```

#### For the Wi-Fi hotspot

To disable this setting for the PlanktoScope's Wi-Fi hotspots, run the following commands in the Cockpit Terminal at <http://planktoscope.local/admin/cockpit/system/terminal> (which you should log in to with the username `pi` and the `pi` user's password, which is `copepode` by default) and then restart the PlanktoScope:

```
forklift pallet disable-deployment-feature host/networking/networkmanager-hotspot dhcp-default-route
forklift pallet stage --no-cache-img
```

To revert this setting back to the default behavior (which is for the PlanktoScope to advertise itself as a router with internet access, so that the PlanktoScope can share its internet access with all connected devices), run the following commands in the Cockpit Terminal and then restart the PlanktoScope:

```
forklift pallet enable-deployment-feature host/networking/interface-forwarding dhcp-default-route
forklift pallet stage --no-cache-img
```

## Secure your PlanktoScope

This section provides instructions on various things you may want to do to improve the networking-related security of your PlanktoScope.

### Change the `pi` user's password

You can log in to the Cockpit system administration dashboard as the `pi` user with that user's password (which is `copepode` by default), and you can also log in to the PlanktoScope via SSH as the `pi` user with that same password. You may want to change the `pi` user to have some other password, in order to limit who can log in as the `pi` user. You can do this in the Cockpit account management interface at <http://planktoscope.local/admin/cockpit/users#/pi>.

### Disable the Wi-Fi hotspot

Your PlanktoScope can make two separate Wi-Fi hotspots: one from the internal Wi-Fi module of your PlanktoScope's Raspberry Pi computer, and another from a USB Wi-Fi dongle plugged into the Raspberry Pi computer (but only when such a dongle exists). These hotspots can be enabled or disabled separately or together.

Note that disabling the hotspots does not affect whether the PlanktoScope is able to connect to external Wi-Fi networks: if the PlanktoScope is already configured to connect to such networks, then it will continue attempting to connect to them.

#### Disable both hotspots together

The simplest way to disable both hotspots together is to run the following commands in the Cockpit Terminal at <http://planktoscope.local/admin/cockpit/system/terminal> (which you should log in to with the username `pi` and the `pi` user's password, which is `copepode` by default) and then restart the PlanktoScope:

```
forklift pallet disable-deployment host/networking/networkmanager-hotspot
forklift pallet stage --no-cache-img
```

!!! warning

    Because you can only undo this configuration change by accessing the PlanktoScope's software, we only recommend configuring your PlanktoScope to disable its Wi-Fi hotspots if 1) you also have a way to connect your device to the PlanktoScope via an Ethernet cable or 2) you can connect to the PlanktoScope when it's connected to an existing Wi-Fi network.

To undo this change (and allow the hotspots to be enabled or disabled separately), run the following commands in the Cockpit Terminal and then restart the PlanktoScope:

```
forklift pallet enable-deployment host/networking/networkmanager-hotspot
forklift pallet stage --no-cache-img
```

#### Disable the internal Wi-Fi module's hotspot

To disable the PlanktoScope's Wi-Fi hotspot, run the following commands in the Cockpit Terminal at <http://planktoscope.local/admin/cockpit/system/terminal> (which you should log in to with the username `pi` and the `pi` user's password, which is `copepode` by default) and then restart the PlanktoScope:

```
forklift pallet disable-deployment-feature host/networking/networkmanager-hotspot wlan0
forklift pallet stage --no-cache-img
```

To revert your changes back to the default behavior (which is for the PlanktoScope to make its own Wi-Fi hotspot when it doesn't detect any known existing Wi-Fi networks to connect to with the internal Wi-Fi module), run the following commands in the Cockpit Terminal and then restart the PlanktoScope:

```
forklift pallet enable-deployment-feature host/networking/networkmanager-hotspot wlan0
forklift pallet stage --no-cache-img
```

!!! warning

    Because you can only undo this configuration change by accessing the PlanktoScope's software, we only recommend configuring your PlanktoScope to disable its internal Wi-Fi module's hotspot if 1) you also have a way to connect your device to the PlanktoScope via an Ethernet cable or 2) you can connect to the PlanktoScope when it's connected to an existing Wi-Fi network or 3) you also have a USB Wi-Fi dongle which can create a Wi-Fi hotspot.

#### Disable the USB Wi-Fi dongle's hotspot

The instructions are the same as for the internal Wi-Fi module's hotspot, except you should replace `wlan0` with `wlan1` in the commands listed above.

### Change the Wi-Fi hotspot's password

Your PlanktoScope has two files specifying the passwords of the Wi-Fi hotspot(s) it can generate: one file for the hotspot which is generated by the internal Wi-Fi module of your PlanktoScope's Raspberry Pi computer, and a different file for the hotspot which is generated by a USB Wi-Fi dongle plugged into the Raspberry Pi computer when such a dongle exists. You can change the names of both of these hotspots, or you can change the name of just one of them. If you don't have a USB Wi-Fi dongle, you can safely ignore the instructions for it.

#### Change the password of the internal Wi-Fi module's hotspot

To change the password of the PlanktoScope's Wi-Fi hotspot away from the default of `copepode`, edit the file at `/etc/NetworkManager/system-connections.d/wlan0-hotspot/51-wifi-security-password.nmconnection`. For example, you can do this by opening the file editor at <http://planktoscope.local/admin/fs/files/etc/NetworkManager/system-connections.d/wlan0-hotspot/51-wifi-security-password.nmconnection> . To apply your changes, restart the PlanktoScope.

To revert your changes back to the default password, we recommend deleting the file at `/var/lib/overlays/overrides/etc/NetworkManager/system-connections.d/wlan0-hotspot/51-wifi-security-password.nmconnection`. For example, you can do this in the file browser at <http://planktoscope.local/admin/fs/files/var/lib/overlays/overrides/etc/NetworkManager/system-connections.d/wlan0-hotspot/> . Then restart the PlanktoScope immediately.

#### Change the password of the USB Wi-Fi dongle's hotspot

The instructions are the same as for the internal Wi-Fi module's hotspot, except you should replace `wlan0` with `wlan1` in all file paths and URLs mentioned above.

### Make the firewall more restrictive

The PlanktoScope has an internal firewall for network connections. By default, the PlanktoScope's firewall is configured to allow access to various specific ports:

1. for devices connected directly to the PlanktoScope (which are in the `nm-shared` firewall zone) by Ethernet cable or through the PlanktoScope's Wi-Fi hotspot

2. for devices on the same Local Area Network (LAN) as the PlanktoScope (which are all in the `public` firewall zone), if the PlanktoScope is connected to an Ethernet/Wi-Fi router

In both of these firewall zones, the firewall blocks access to any ports which are not explicitly allowed by the PlanktoScope's configuration. For usability/recoverability/operability reasons, you will probably want to maintain the default level of access to all of the PlanktoScope's software from directly-connected devices (i.e. in the `nm-shared` zone); but for security reasons, you may want to further restrict access for devices from an untrusted LAN (i.e. in the `public` zone).

You can view the currently-active firewall rules in Cockpit's firewall configuration panel at <http://planktoscope.local/admin/cockpit/network/firewall>; however, we do not recommend changing rules in that panel if you are able to instead follow the instructions provided below. This is because making changes with Cockpit will override all future changes which would otherwise be made with Forklift (e.g. in future software updates). If you would like to relax firewall restrictions (for example by opening up additional ports), you should instead add drop-in configuration files (as XML fragments) in `/etc/firewalld/zones.d/nm-shared/` and `/etc/firewalld/zones.d/public/` and then reboot to apply your changes; in the future, we create another operation guide with more detailed instructions for how to do this.

#### Restrict access in the `public` zone

It is easy to restrict access in the `public` firewall zone for the following ports/protocols:

- SSH (port 22), whose access is provided by a Forklift package deployment named `host/sshd`: restricting access to this will prevent access to the PlanktoScope over SSH from devices in the `public` zone.
- Direct-access fallback for the Cockpit system administration dashboard (port 9090), whose access is provided by a Forklift package deployment named `host/cockpit`: restricting direct access to this will prevent access to the PlanktoScope's Cockpit dashboard from devices in the `public` zone. Note that by default an HTTP reverse proxy also provides indirect access to Cockpit through port 80.
- MQTT (port 1883), whose access is provided by a Forklift package deployment named `infra/mosquitto`: restricting access to this will prevent access to the PlanktoScope's [MQTT API](../reference/software/interfaces/mqtt.md) from devices in the `public` zone.
- HTTP (port 80), whose access is provided by a Forklift package deployment named `infra/caddy-ingress`: restricting access to this will prevent access to the PlanktoScope's [web browser user interfaces](../reference/software/architecture/os.md#user-interface) and HTTP APIs from devices in the `public` zone.
- mDNS (port 5353), whose access is provided by a Forklift package deployment named `host/networking/avahi-daemon`: restricting access to this will prevent devices in the `public` zone from discovering the PlanktoScope's IP address(es) by querying the PlanktoScope's mDNS hostnames (i.e. hostnames ending in `.local`, such as `planktoscope.local`).
- ICMP, whose access is provided by a Forklift package deployment named `host/networking/networkmanager`: restricting access this will prevent devices in the `public` zone from pinging the PlanktoScope to check whether it exists.

To restrict access for the `public` zone for one or more of these ports/protocols, run the following commands in the Cockpit Terminal at <http://planktoscope.local/admin/cockpit/system/terminal> (which you should log in to with the username `pi` and the `pi` user's password, which is `copepode` by default), replacing the instances of `{package deployment}` with the names of the various package deployments providing access to ports/protocols which you want to restrict:

```
forklift pallet disable-deployment-feature {package deployment} firewall-allow-public
forklift pallet disable-deployment-feature {package deployment} firewall-allow-public
forklift pallet disable-deployment-feature {package deployment} firewall-allow-public
forklift pallet stage --no-cache-img
```

For example, to restrict ports 22 and 9090, you would run the following commands:

```
forklift pallet disable-deployment-feature host/sshd firewall-allow-public
forklift pallet disable-deployment-feature host/cockpit firewall-allow-public
forklift pallet stage --no-cache-img
```

After running these commands, you can apply your changes by rebooting.

!!! warning

    It is easy to restrict access so much that you will become unable to access the PlanktoScope over its network interfaces through a router connected to your PlanktoScope. You should make sure you have some way to directly connect to the PlanktoScope, e.g. by a direct Ethernet cable connection or with a keyboard and display.

To undo your changes, run the following commands, replacing the instances of `{package deployment}` with the names of the various package deployments which you want to restore access to:

```
forklift pallet enable-deployment-feature {package deployment} firewall-allow-public
forklift pallet enable-deployment-feature {package deployment} firewall-allow-public
forklift pallet enable-deployment-feature {package deployment} firewall-allow-public
forklift pallet stage --no-cache-img
```

For example, to restore access to ports 22 and 9090, you would run the following commands:

```
forklift pallet enable-deployment-feature host/sshd firewall-allow-public
forklift pallet enable-deployment-feature host/cockpit firewall-allow-public
forklift pallet stage --no-cache-img
```

After running these commands, you should apply the resulting changes by rebooting.

#### Restrict access in the `nm-shared` zone

If you really want to limit access in the `nm-shared` zone, you can follow the above instructions given for the `public` zone but replace `firewall-allow-public` with `firewall-allow-nm-shared`.

!!! warning

    It is easy to restrict access so much that you will become unable to access the PlanktoScope over its network interfaces from devices with direct network connections to the PlanktoScope. If that happens, then the only way to access your PlanktoScope (e.g. to restore its previous settings) will be by connecting a display and keyboard to your PlanktoScope.

### Disable all access to privileged web browser apps

The following web browser apps provide full administrative (i.e. root or superuser) access to the system on port 80 via the HTTP reverse-proxy server:

- Cockpit: a system administration dashboard which includes a terminal for running arbitrary commands (including privileged commands with `sudo`); access to this is provided by a feature flag named `frontend` in a Forklift package deployment named `apps/cockpit`.
- System file manager: provides privileged access for viewing and editing arbitrary files across the entire filesystem; access to this is provided by a feature flag named `frontend` in a Forklift package deployment named `apps/filebrowser-root`.
- Node-RED dashboard editor: provides a mechanism for running arbitrary privileged commands; access to this is provided by a feature flag named `editor` in a Forklift package deployment named `apps/ps/node-red-dashboard`.

To disable access to one or more of these apps, run the following commands in the Cockpit Terminal at <http://planktoscope.local/admin/cockpit/system/terminal> (which you should log in to with the username `pi` and the `pi` user's password, which is `copepode` by default), replacing the instances of `{package deployment}` with the names of the various package deployments providing access which you want to restrict, and replacing the instances of `{feature flag}` with the names of the feature flags which specifically provide the access you want to restrict:

```
forklift pallet disable-deployment-feature {package deployment} {feature flag}
forklift pallet disable-deployment-feature {package deployment} {feature flag}
forklift pallet disable-deployment-feature {package deployment} {feature flag}
forklift pallet stage --no-cache-img
```

For example, to restrict access to the system file manager and the Node-RED dashboard editor, you would run the following commands:

```
forklift pallet disable-deployment-feature apps/filebrowser-root frontend
forklift pallet disable-deployment-feature apps/ps/node-red-dashboard editor
forklift pallet stage --no-cache-img
```

After running these commands, you can apply your changes by rebooting. Note that the landing page will still link to those apps, but the links won't work anymore.

To undo your changes, run the following commands, replacing the instances of `{package deployment}` and `{feature flag}` with the names of the various package deployments and their respective feature flags which you want to re-enable to restore access:

```
forklift pallet enable-deployment-feature {package deployment} {feature flag}
forklift pallet enable-deployment-feature {package deployment} {feature flag}
forklift pallet enable-deployment-feature {package deployment} {feature flag}
forklift pallet stage --no-cache-img
```

For example, to restore access to the system file manager and the Node-RED dashboard editor, you would run the following commands:

```
forklift pallet enable-deployment-feature apps/filebrowser-root frontend
forklift pallet enable-deployment-feature apps/ps/node-red-dashboard editor
forklift pallet stage --no-cache-img
```

After running these commands, you should apply the resulting changes by rebooting.

## Allow access to Cockpit from additional domain names or IP addresses

For security reasons, [Cockpit](http://planktoscope.local/admin/cockpit/) only allows you to access Cockpit from a list of known domain names and ports (e.g. [planktoscope.local](http://planktoscope.local/admin/cockpit/) and [planktoscope.local:9090](http://planktoscope.local:9090/admin/cockpit/)) and known IP addresses and ports (e.g. [192.168.4.1](http://192.168.4.1/admin/cockpit/) and [192.168.4.1:9090](http://192.168.4.1:9090/admin/cockpit/)). If you have connected the PlanktoScope to a network or to the internet so that you can reach the PlanktoScope from some other domain name or IP address, and you also want to access Cockpit from that other domain name or IP address, then you will need to add that domain name or IP address into the list of Cockpit's known domain names and ports.

To add additional known domain names or IP addresses where Cockpit should be accessible, create and edit a file at `/etc/cockpit/origins.d/`, following the instructions/notes at `/etc/cockpit/origins.d/10-README` and referring to `/etc/cockpit/origins.d/20-localhost` as a reference example. For example, you can do this in the file browser at <http://planktoscope.local/admin/fs/files/etc/cockpit/origins.d/>, and you can view the instructions/notes at <http://planktoscope.local/admin/fs/files/etc/cockpit/origins.d/10-README>, and you can view the reference example at <http://planktoscope.local/admin/fs/files/etc/cockpit/origins.d/20-localhost> . To apply your changes, restart the PlanktoScope.

To revert your changes back to the default list of known domain names and IP addresses where Cockpit can be accessed, we recommend deleting the files in `/var/lib/overlays/overrides/etc/cockpit/origins.d/` and then restarting the PlanktoScope. For example, you can do this in the file browser at <http://planktoscope.local/admin/fs/files/var/lib/overlays/overrides/etc/cockpit/origins.d/> . Then restart the PlanktoScope immediately.

## Change your PlanktoScope's name

Your PlanktoScope has a semi-unique machine name which by default is stably and automatically generated from your Raspberry Pi's semi-unique serial number. This machine name has format `{adjective}-{noun}-{number up to five digits long}`, e.g. `metal-slope-23501` or `safe-minute-6738`. The machine name is used to generate the hostname of the PlanktoScope with the format `pkscope-{machine-name}`; and the PlanktoScope's hostname is also used to generate the name (to be precise, the SSID) of its Wi-Fi hotspot as well as the machine-specific mDNS URLs you can use to access the PlanktoScope (e.g. [pkscope-metal-slope-23501.local](http://pkscope-metal-slope-23501.local) or [pkscope-safe-minute-6738.local](http://pkscope-safe-minute-6738.local)).

If you're unhappy with these names, you can change any or all of them.

### Change the machine name

To change your PlanktoScope's machine name, delete the file at `/etc/machine-name` and then create and edit a new file at `/etc/machine-name`; the contents of that new file should be the name you want to assign to the PlanktoScope. For example, you can do this in the file browser at <http://planktoscope.local/admin/fs/files/etc/> . To apply your changes, restart the PlanktoScope. Note: this change will also affect your PlanktoScope's hostname and Wi-Fi hotspot name, unless you've also customized them separately (as described below).

To revert your changes back to the default auto-generated machine name based on the Raspberry Pi's serial number, delete the file at `/var/lib/overlays/overrides/etc/machine-name` and then restart the PlanktoScope. For example, you can do this in the file browser at <http://planktoscope.local/admin/fs/files/var/lib/overlays/overrides/etc/> . Then restart the PlanktoScope immediately.

### Change the hostname

To change your PlanktoScope's hostname away from the format `{adjective}-{noun}-{number up to five digits long}` without also changing the machine name, edit the file at `/etc/hostname-template`. For example, you can do this by opening the file editor at <http://planktoscope.local/admin/fs/files/etc/hostname-template> . To apply your changes, restart the PlanktoScope. Note: this change will also affect your PlanktoScope's Wi-Fi hotspot name, unless you've also customized it separately (as described below).

To revert your changes back to the default hostname based on the machine name, we recommend deleting the file at `/var/lib/overlays/overrides/etc/hostname-template` and then restarting the PlanktoScope. For example, you can do this in the file browser at <http://planktoscope.local/admin/fs/files/var/lib/overlays/overrides/etc/> . Then restart the PlanktoScope immediately.

### Change the Wi-Fi hotspot name

Your PlanktoScope has two files specifying the names of the Wi-Fi hotspot(s) it can generate: one file for the hotspot which is generated by the internal Wi-Fi module of your PlanktoScope's Raspberry Pi computer, and a different file for the hotspot which is generated by a USB Wi-Fi dongle plugged into the Raspberry Pi computer when such a dongle exists. You can change the names of both of these hotspots, or you can change the name of just one of them. If you don't have a USB Wi-Fi dongle, you can safely ignore the instructions for it.

#### Change the name of the internal Wi-Fi module's hotspot

To change your PlanktoScope's Wi-Fi hotspot name away from the format `{the first 32 characters of the hostname}` without also changing the hostname, edit the file at `/etc/NetworkManager/system-connections-templates.d/wlan0-hotspot/20-ssid.nmconnection`, following the instructions/notes at `/etc/NetworkManager/system-connections-templates.d/wlan0-hotspot/10-README.nmconnection`. For example, you can do this by opening the file editor at <http://home.pkscope/admin/fs/files/etc/NetworkManager/system-connections-templates.d/wlan0-hotspot/20-ssid.nmconnection>, and you can view the instructions/notes at <http://planktoscope.local/admin/fs/files/etc/NetworkManager/system-connections-templates.d/wlan0-hotspot/10-README.nmconnection> . To apply your changes, restart the PlanktoScope.

To revert your changes back to the default Wi-Fi hotspot name based on the hostname, we recommend deleting the file at `/var/lib/overlays/overrides/etc/NetworkManager/system-connections-templates.d/wlan0-hotspot/20-ssid.nmconnection` and then restarting the PlanktoScope. For example, you can do this in the file browser at <http://planktoscope.local/admin/fs/files/var/lib/overlays/overrides/etc/NetworkManager/system-connections-templates.d/wlan0-hotspot/> . Then restart the PlanktoScope immediately.

#### Change the name of the USB Wi-Fi dongle's hotspot

The instructions are the same as for the internal Wi-Fi module's hotspot, except you should replace `wlan0` with `wlan1` in all file paths and URLs mentioned above.
