# Networking guide

By default, your PlanktoScope creates an [isolated Wi-Fi network](./index.md#connect-with-the-planktoscopes-isolated-wi-fi-network) (which we often call "the PlanktoScope's Wi-Fi hotspot network") which devices can connect to in order to access the PlanktoScope's software; and devices can also connect to the PlanktoScope directly [by an Ethernet cable](./index.md#connect-with-an-ethernet-cable). However, you may have reasons to adjust your networking configuration away from this default. This guide provides instructions on how to adjust your networking configuration in various ways.

Currently, all instructions in this guide should be considered as being provided for "advanced users" (and/or for users who are able to ask for help in the PlanktoScope Slack workspace). These instructions will probably change between between successive releases of the PlanktoScope software. All URLs in this guide are written assuming you access your PlanktoScope using [planktoscope.local](http://planktoscope.local) as the domain name; if you need to use a [different domain name](./index.md#access-your-planktoscopes-software) such as [home.pkscope](http://home.pkscope), you should substitute that domain name into the links on this page.

## Adjust your PlanktoScope's Wi-Fi region settings

### Change Wi-Fi hotspot region settings

By default, the PlanktoScope makes its Wi-Fi hotspot network on [WLAN channel](https://en.wikipedia.org/wiki/List_of_WLAN_channels) 8 and in compliance with United States Wi-Fi [regulatory domain](https://en.wikipedia.org/wiki/IEEE_802.11#Regulatory_domains_and_legal_compliance). If your computer/phone/etc.'s connection to the PlanktoScope's Wi-Fi hotspot is unstable and you are operating your PlanktoScope outside the United States, you may need to change your Wi-Fi network's regional settings. For example, if you are operating in France, you should change the Wi-Fi hotspot's [ISO/IEC 3166-1](https://en.wikipedia.org/wiki/ISO_3166-1#Codes)-formatted country code from `US` to `FR`.

To change the regional settings of the PlanktoScope's Wi-Fi hotspot away from the defaults, edit the file at `/etc/hostapd/hostapd.conf.d/50-localization-us.conf`. For example, you can do this by opening the file editor at <http://planktoscope.local/admin/fs/files/etc/hostapd/hostapd.conf.d/50-localization-us.conf> . To apply your changes, restart the PlanktoScope.

To revert your changes back to the default regional settings, we recommend deleting the file at `/var/lib/overlays/overrides/etc/hostapd/hostapd.conf.d/50-localization-us.conf`. For example, you can do this in the file browser at <http://planktoscope.local/admin/fs/files/var/lib/overlays/overrides/etc/hostapd/hostapd.conf.d/> . Then restart the PlanktoScope immediately.

## Connect your PlanktoScope to the internet

To connect your PlanktoScope to the internet, we recommend one of the following options:

1. Plug it into an Ethernet port with internet access.
2. Connect an Android phone/tablet by USB to your PlanktoScope and then enabling USB tethering mode so that the Android device shares its internet access (which can be from the Wi-Fi network it's connected to) to the PlanktoScope. Note: we plan to add support for USB tethering from iOS devices, but we haven't figured out how to do that yet.

Once your PlanktoScope is connected to the internet, by default it will attempt to share its internet access with any devices connected to the PlanktoScope by Wi-Fi or Ethernet.

If you need to connect to a network which requires you to register your PlanktoScope's MAC address (also known as the "hardware address" of your PlanktoScope's network adapter(s)), please refer to [a subsection below](#check-your-planktoscopes-mac-addresses).

### Connect your PlanktoScope to an existing Wi-Fi network

It's also possible to connect the PlanktoScope to an existing Wi-Fi network with internet access, but the PlanktoScope will be unable to make its Wi-Fi hotspot network while it is connected to an existing Wi-Fi network. Then, as long as the PlanktoScope is within range of that Wi-Fi network, the PlanktoScope software is only accessible either if 1) the existing Wi-Fi network (including its firewall settings) is configured to allow you to access the PlanktoScope via mDNS and your device and web browser support mDNS URLs (i.e. URLs ending in `.local`, like <http://planktoscope.local>) or if 2) you connect your device to the PlanktoScope via an Ethernet cable.

!!! info

    To be precise, the PlanktoScope will ping google.com to check if it can access the internet once it connects to an existing Wi-Fi network; if it still cannot reach google.com after ~10 failed attempts over a period of ~20-30 seconds, then the PlanktoScope will disconnect from the Wi-Fi network and instead make its own Wi-Fi hotspot. This is meant to help prevent PlanktoScopes from getting stuck when connecting to Wi-Fi networks whose firewall settings do not allow the PlanktoScope to access the network, as the PlanktoScopes may be entirely inaccessible on such networks.

Once you take the PlanktoScope out of range of the existing Wi-Fi network, within approximately two minutes it should automatically revert to making its own Wi-Fi hotspot network. If you then take the PlanktoScope back in range of the existing Wi-Fi network, within approximately two minutes it should automatically attempt to connect to the existing Wi-Fi network again (and, if it succeeds, it will stop the Wi-Fi hotspot network).

!!! warning

    Because you can only undo this configuration change by accessing the PlanktoScope's software (or by running a Linux computer which can open and edit the `/etc/wpa_supplicant/wpa_supplicant.conf` configuration file for Wi-Fi network connections in your PlanktoScope's SD card), we only recommend configuring your PlanktoScope to connect to an existing Wi-Fi network if 1) you also have a way to connect your device to the PlanktoScope via an Ethernet cable or if 2) you are also able to run your PlanktoScope in a location beyond the range of the existing Wi-Fi network (as that the PlanktoScope will revert to making a Wi-Fi hotspot when it cannot detect the existing Wi-Fi network) or if 3) you have a Linux computer which is able to edit files on your PlanktoScope's SD card.

!!! warning

    Before you make any changes, you should first write down your PlanktoScope's machine name (which is listed in your PlanktoScope's landing page), and you should also check whether your web browser allows you to use the machine-specific URL of format `http://pkscope-{machine-name}.local` for accessing your PlanktoScope's landing page. This is because other URLs from our [standard software setup guide](../setup/software/standard-install.md#connect-to-the-planktoscope) and our [basic operation guide](./index.md#access-your-planktoscopes-software) which you may be more familiar with, such as <http://planktoscope.local> or <http://home.pkscope> or <http://192.168.4.1>, will not work for accessing your PlanktoScope through the existing Wi-Fi network! Only a machine-specific URL of format `http://pkscope-{machine-name}.local` may work.

For now, the only way we recommend for connecting your PlanktoScope to an existing Wi-Fi network is by editing the `/etc/wpa_supplicant/wpa_supplicant.conf` file; the PlanktoScope's Node-RED dashboard has a "Wifi" page which is partially broken (including writing an error message into the `/etc/wpa_supplicant/wpa_supplicant.conf` file if you attempt to add a Wi-Fi network without a password) and will be removed in a future release of the PlanktoScope's software. For example, you can edit the `wpa_supplicant.conf` file by opening the file editor at <http://planktoscope.local/admin/fs/files/etc/wpa_supplicant/wpa_supplicant.conf> . After saving your changes to that file, you can apply them by either 1) using Cockpit's service manager to start the `autohotspot` service (e.g. at <http://planktoscope.local/admin/cockpit/system/services#/autohotspot.service> ), 2) waiting a few minutes for the `autohotspot` service to automatically run again, or 3) rebooting your PlanktoScope.

You can find more information on how to edit the `wpa_supplicant.conf` file in [this guide](https://fleetstack.io/blog/raspberry-pi-etc-wpa-supplicant-wpa-supplicant-conf-file). For quick reference, here are some network configuration snippets from that link:

```
# For password-protected networks:
network={
  ssid="YourNetworkSSID"
  psk="YourNetworkPassword"
  key_mgmt=WPA-PSK
}

# For passwordless networks:
network={
  ssid="YourNetworkSSID"
  key_mgmt=NONE
}
```



Once your PlanktoScope is connected to an existing Wi-Fi network, you should try to access it via your PlanktoScope's machine-specific mDNS URL, which has format `http://pkscope-{machine-name}.local`. Note that this may fail if your Wi-Fi network has restrictive firewall settings, in which case you will only be able to connect to your PlanktoScope directly via Ethernet cable. Note also that this URL only works if your device and web browser both support mDNS.

### Check your PlanktoScope's MAC addresses

If you need to check the MAC addresses of your PlanktoScope's network interfaces, you can open an auto-generated report of MAC addresses at `/run/mac-address.yml`, for example by opening the file viewer at <http://planktoscope.local/admin/fs/files/run/mac-addresses.yml>. That file viewer is also linked to from your PlanktoScope's landing page, in a link named "MAC address viewer" in the "For advanced users" section of the landing page.

Usually you will only care about the MAC addresses for `wlan0` or `eth0`, which are the built-in Wi-Fi module and Ethernet port of the PlanktoScope's embedded Raspberry Pi computer, respectively. If you connect additional network adapters (such as a USB Wi-Fi dongle, an Ethernet-to-USB adapter, or a phone in USB tethering mode), then you may also see additional network interfaces named something like `wlan1`, `eth1`, or `usb0` around two minutes later.

Every two minutes, your PlanktoScope will refresh the list of MAC addresses, in case you connect any new network adapters to your PlanktoScope or disconnect any network adapters.

## Connect your client device to the internet while your PlanktoScope is not connected to the internet

If you can connect your PlanktoScope to the internet, then it will behave like a network router, sharing its internet access with all devices connected to the PlanktoScope; that's the easiest way to have your computer/phone/etc. connected to the PlanktoScope while still being able to access the internet. However, it is often useful to connect a computer simultaneously both to the internet and to a PlanktoScope which does not have internet access. You can do this through any of the following possible approaches:

1. Have your computer connect to the internet by an existing Wi-Fi network, and then connect your computer by Ethernet cable to the PlanktoScope.
2. Have your computer connect to the internet by an Ethernet cable, and then connect your computer to the PlanktoScope's Wi-Fi hotspot.
3. Connect a phone/tablet by USB to your computer and enable your phone/tablet's USB tethering mode to share its internet access to your computer, and then connect your computer to the PlanktoScope's Wi-Fi hotspot or to an Ethernet cable plugged into the PlanktoScope.
4. Add one or two USB Wi-Fi dongles to your computer so that it has a total of two Wi-Fi adapters (one of which may be internal to your computer) and thus can connect to two Wi-Fi networks simultaneously; then configure your computer to connect to the internet by an existing Wi-Fi network using one of the Wi-Fi adapters and to simultaneously connect to the PlanktoScope's Wi-Fi hotspot using the other Wi-Fi adapter.
5. Add one or two USB Ethernet adapters to your computer so that it has a total of two Ethernet adapters (one of which may be internal to your computer) and thus can connect to two Ethernet ports simultaneously; then connect one of your computer's Ethernet adapters to an Ethernet port with internet access, and connect your computer's other Ethernet adapter to the PlanktoScope.
6. Connect both your computer and the PlanktoScope to an [Ethernet switch](https://en.wikipedia.org/wiki/Network_switch), then connect your computer to the internet by an existing Wi-Fi network. Note 1: an Ethernet switch is a different kind of device than an Ethernet router. Note 2: if you then connect your Ethernet switch to an Ethernet or Wi-Fi router, then the the PlanktoScope will only be accessible if the router's firewall allows network connections to the PlanktoScope from other devices on the router's Local Area Network (LAN).

### Don't allow the PlanktoScope to be used as a default gateway to the internet

Because by default your PlanktoScope is configured to act as a router so that it can share its internet access with all connected devices, it will advertise itself as a default gateway to the internet, so that connected devices will use the PlanktoScope as a network router for internet access. However, some computers (e.g. those running macOS or Windows) may behave as if the PlanktoScope is the *only* router with internet access even if the PlanktoScope actually has no internet access while the computer is also connected to a router for another network which *does* have internet access; then such computers will fail to access the internet while they're connected to the PlanktoScope.

You can work around this unfortunate behavior of your computer's operating system by disabling a setting in the PlanktoScope's networking configuration so that the PlanktoScope no longer advertises itself as a router with internet access; note that doing so will prevent the PlanktoScope from being able to share its own internet access with connected devices as long as this setting is disabled. To disable this setting, run the following commands in the Cockpit Terminal at <http://planktoscope.local/admin/cockpit/system/terminal> (which you should log in to with the username `pi` and the `pi` user's password, which is `copepode` by default) and then restart the PlanktoScope:

```
forklift pallet disable-deployment-feature host/networking/interface-forwarding planktoscope-dhcp-default-route
forklift pallet stage --no-cache-img
```

To revert this setting back to the default behavior (which is for the PlanktoScope to advertise itself as a router with internet access, so that the PlanktoScope can share its internet access with all connected devices), run the following commands in the Cockpit Terminal and then restart the PlanktoScope:

```
forklift pallet enable-deployment-feature host/networking/interface-forwarding planktoscope-dhcp-default-route
forklift pallet stage --no-cache-img
```

## Secure your PlanktoScope

This section provides instructions on various things you may want to do to improve the networking-related security of your PlanktoScope.

### Change the Wi-Fi hotspot's password

To change the password of the PlanktoScope's Wi-Fi hotspot away from the default of `copepode`, edit the file at `/etc/hostapd/hostapd.conf.d/30-auth-30-planktoscope-passphrase.conf`. For example, you can do this by opening the file editor at <http://planktoscope.local/admin/fs/files/etc/hostapd/hostapd.conf.d/30-auth-30-planktoscope-passphrase.conf> . To apply your changes, restart the PlanktoScope.

To revert your changes back to the default password, we recommend deleting the file at `/var/lib/overlays/overrides/etc/hostapd/hostapd.conf.d/30-auth-30-planktoscope-passphrase.conf`. For example, you can do this in the file browser at <http://planktoscope.local/admin/fs/files/var/lib/overlays/overrides/etc/hostapd/hostapd.conf.d/> . Then restart the PlanktoScope immediately.

### Disable the Wi-Fi hotspot

To disable the PlanktoScope's Wi-Fi hotspot, run the following commands in the Cockpit Terminal at <http://planktoscope.local/admin/cockpit/system/terminal> (which you should log in to with the username `pi` and the `pi` user's password, which is `copepode` by default) and then restart the PlanktoScope:

```
forklift pallet disable-deployment host/networking/autohotspot
forklift pallet stage --no-cache-img
```

To revert your changes back to the default behavior (which is for the PlanktoScope to make its own Wi-Fi hotspot when it doesn't detect any known existing Wi-Fi networks to connect to), run the following commands in the Cockpit Terminal and then restart the PlanktoScope:

```
forklift pallet enable-deployment host/networking/autohotspot
forklift pallet stage --no-cache-img
```

!!! warning

    Because you can only undo this configuration change by accessing the PlanktoScope's software, we only recommend configuring your PlanktoScope to disable its Wi-Fi hotspot if 1) you also have a way to connect your device to the PlanktoScope via an Ethernet cable or 2) you can connect to the PlanktoScope when it's connected to an existing Wi-Fi network.

## Allow access to Cockpit from additional domain names or IP addresses

For security reasons, [Cockpit](http://planktoscope.local/admin/cockpit/) only allows you to access Cockpit from a list of known domain names and ports (e.g. [planktoscope.local](http://planktoscope.local/admin/cockpit/) and [planktoscope.local:9090](http://planktoscope.local:9090/admin/cockpit/)) and known IP addresses and ports (e.g. [192.168.4.1](http://192.168.4.1/admin/cockpit/) and [192.168.4.1:9090](http://192.168.4.1:9090/admin/cockpit/)). If you have connected the PlanktoScope to a network or to the internet so that you can reach the PlanktoScope from some other domain name or IP address, and you also want to access Cockpit from that other domain name or IP address, then you will need to add that domain name or IP address into the list of Cockpit's known domain names and ports.

To add additional known domain names or IP addresses where Cockpit should be accessible, create and edit a file at `/etc/cockpit/origins.d/`, following the instructions/notes at `/etc/cockpit/origins.d/10-README` and referring to `/etc/cockpit/origins.d/20-localhost` as a reference example. For example, you can do this in the file browser at <http://planktoscope.local/admin/fs/files/etc/cockpit/origins.d/>, and you can view the instructions/notes at <http://home.pkscope/admin/fs/files/etc/cockpit/origins.d/10-README>, and you can view the reference example at <http://home.pkscope/admin/fs/files/etc/cockpit/origins.d/20-localhost> . To apply your changes, restart the PlanktoScope.

To revert your changes back to the default list of known domain names and IP addresses where Cockpit can be accessed, we recommend deleting the files in `/var/lib/overlays/overrides/etc/cockpit/origins.d/` and then restarting the PlanktoScope. For example, you can do this in the file browser at <http://planktoscope.local/admin/fs/files/var/lib/overlays/overrides/etc/cockpit/origins.d/> . Then restart the PlanktoScope immediately.

## Change your PlanktoScope's name

Your PlanktoScope has a semi-unique machine name which by default is stably and automatically generated from your Raspberry Pi's semi-unique serial number. This machine name has format `{adjective}-{noun}-{number up to five digits long}`, e.g. `metal-slope-23501` or `safe-minute-6738`. The machine name is used to generate the hostname of the PlanktoScope with the format `pkscope-{machine-name}`; and the PlanktoScope's hostname is also used to generate the name (to be precise, the SSID) of its Wi-Fi hotspot as well as the machine-specific mDNS URLs you can use to access the PlanktoScope (e.g. [metal-slope-23501.local](http://metal-slope-23501.local) or [safe-minute-6738.local](http://safe-minute-6738.local)).

### Change the machine name

To change your PlanktoScope's machine name, create and edit a file at `/etc/machine-name`. For example, you can do this in the file browser at <http://planktoscope.local/admin/fs/files/etc/> . To apply your changes, restart the PlanktoScope.

To revert your changes back to the default auto-generated machine name based on the Raspberry Pi's serial number, delete the file at `/var/lib/overlays/overrides/etc/machine-name` and then restart the PlanktoScope. For example, you can do this in the file browser at <http://planktoscope.local/admin/fs/files/var/lib/overlays/overrides/etc/> . Then restart the PlanktoScope immediately.

### Change the hostname

To change your PlanktoScope's hostname away from the format `{adjective}-{noun}-{number up to five digits long}` without also changing the machine name, edit the file at `/etc/hostname-template`. For example, you can do this by opening the file editor at <http://planktoscope.local/admin/fs/files/etc/hostname-template> . To apply your changes, restart the PlanktoScope.

To revert your changes back to the default hostname based on the machine name, we recommend deleting the file at `/var/lib/overlays/overrides/etc/hostname-template` and then restarting the PlanktoScope. For example, you can do this in the file browser at <http://planktoscope.local/admin/fs/files/var/lib/overlays/overrides/etc/> . Then restart the PlanktoScope immediately.

### Change the Wi-Fi hotspot name

To change your PlanktoScope's Wi-Fi hotspot name away from the format `{the first 32 characters of the hostname}` without also changing the hostname, edit the file at `/etc/hostapd/hostapd.conf-templates.d/20-ssid.conf`, following the instructions/notes at `/etc/hostapd/hostapd.conf-templates.d/10-README.conf`. For example, you can do this by opening the file editor at <http://planktoscope.local/admin/fs/files/etc/hostapd/hostapd.conf-templates.d/20-ssid.conf>, and you can view the instructions/notes at <http://home.pkscope/admin/fs/files/etc/hostapd/hostapd.conf-templates.d/10-README.conf> . To apply your changes, restart the PlanktoScope.

To revert your changes back to the default Wi-Fi hotspot name based on the hostname, we recommend deleting the file at `/var/lib/overlays/overrides/etc/hostapd/hostapd.conf-templates.d/20-ssid.conf` and then restarting the PlanktoScope. For example, you can do this in the file browser at <http://planktoscope.local/admin/fs/files/var/lib/overlays/overrides/etc/hostapd/hostapd.conf-templates.d/> . Then restart the PlanktoScope immediately.
