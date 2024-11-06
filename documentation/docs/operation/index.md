# Operation

This page provides basic instructions for operating your PlanktoScope.

![getting started](../images/getting_started/BWS01556.JPG)

## Connect directly to your PlanktoScope

In order to operate your PlanktoScope, you will need to connect to your PlanktoScope from a separate device (a computer, tablet, or phone) with a web browser. If this is your first time setting up or connecting to your PlanktoScope, you will need to set up a direct network connection between your computer and your PlanktoScope.

### Connect with an Ethernet cable

You can connect your computer to the PlanktoScope by plugging an Ethernet cable between your computer and your PlanktoScope's Raspberry Pi.

### Connect with the PlanktoScope's isolated Wi-Fi network

Unless you have already configured your PlanktoScope to connect to an existing Wi-Fi network, your PlanktoScope will create its own isolated Wi-Fi network (like a Wi-Fi hotspot, but without internet access). The Wi-Fi network created by your PlanktoScope should appear on your computer's list of available Wi-Fi networks a few minutes after you turn on power to your PlanktoScope.

![wifi-network.png](images/wifi-network.png)

As you can see, the name of your PlanktoScope's Wi-Fi network will be of the format `pkscope-{random word}-{random word}-{random number}`. This name corresponds exactly to the serial number of the Raspberry Pi computer in your PlanktoScope, so it is a unique Wi-Fi network name; and the unique name of your machine has format `{random-word}-{random-word}-{random number}`, which is just the name of the Wi-Fi network but without the `pkscope-` prefix (e.g. `chain-list-27764`). You should connect to the Wi-Fi network specific to your PlanktoScope.

Unless you have changed the password of your PlanktoScope's Wi-Fi network, the password should be `copepode`.

### Access your PlanktoScope's software

Once you connect your computer to your PlanktoScope, you will need to access your PlanktoScope's software from a web browser on your computer. You should try opening the following URLs in your web browser (try opening them in the following order, and just use the first one which works):

- <http://planktoscope.local> (this should work unless you're on a device and web browser without mDNS support; notably, older versions of Android do not have mDNS support)
- <http://pkscope.local> (this should work unless you're on a device and web browser without mDNS support; notably, older versions of Android do not have mDNS support)
- <http://home.pkscope> (this should work unless your web browser is configured to use a Private DNS provider)
- <http://192.168.4.1> (this should always work)
- <http://192.168.5.1> (this should always work)

!!! tip

    If you know the machine name of your PlanktoScope (which has format `{random-word}-{random-word}-{random number}`, e.g. `chain-list-27764`, you can also try the following URLs after replacing `{machine-name}` with the actual machine name of your PlanktoScope:
    
    `http://pkscope-{machine-name}.local` (this should work unless you're on a device and web browser without mDNS support; notably, older versions of Android do not have mDNS support)
    
    `http://{machine-name}.pkscope` (this should work unless your web browser is configured to use a Private DNS provider)
    
    You will need to use a URL with your PlanktoScope's machine name if your computer has network connections to multiple PlanktoScopes, e.g. via multiple Ethernet cables. In such a situation, using <http://home.pkscope> or <http://pkscope.local> may cause you to access the software for a different PlanktoScope connected to your computer than the one you had intended to access.

!!! warning

    You may encounter older documents which ask you to connect to <http://planktoscope.local:1880/ui>, which is the URL to use for software version 2.3 and even older versions. That link does not work on software versions newer than v2.3; instead, you should use the links listed above.

One of the above URLs should work, and your web browser should show a landing page with a list of links:

![landing-page.png](images/landing-page.png)

You should click on the "Node-RED dashboard" link; this will open a new tab with the primary interface for operating your PlanktoScope. Once you have opened the Node-RED dashboard, you should proceed to our [User interface guide](user-interface.md) to understand how to use it.

## How to image plankton

Before doing an acquisition, you will need to collect targets. There are several ways to do this, and you probably already have a source nearby (in a culture if you are working in a lab).

However, if you have access to a body of water (even a tiny lake or river is enough), you can build yourself a plankton net to collect a sample. Once the sample is collected, either pump it with a syringe that you connect to the machine, or dip one of the silicone tube inside the sample tube you have.

You can then do an acquisition run. **This is the best way to learn about the machine and this process!**

!!! warning

    After doing an acquisition, the machine should be cleaned, especially in the fluidic part. One good way to do this is to first flush the machine with clear water (distilled if possible). You can then push through a 5-10% bleach solution, or some alcohol.

If needed you can also clean the outside of the objective lens with a soft cloth. You can do the same on the flow cell if there are traces of finger on it too.

For quantitative imaging of water samples, refer to the following protocols published by members of the PlanktoScope community:

- "[Planktoscope protocol for plankton imaging V.3](https://www.protocols.io/view/planktoscope-protocol-for-plankton-imaging-bp2l6bq3zgqe/v3)" for software v2.3+ and hardware v2.5. A [PDF copy](protocol-v3.pdf) of this protocol is also available for offline use.
- "[Planktoscope protocol for plankton imaging V.2](https://www.protocols.io/view/planktoscope-protocol-for-plankton-imaging-bp2l6bq3zgqe/v2)" for software v2.3+ and hardware v2.5. A [PDF copy](protocol-v2.pdf) of this protocol is also available for offline use.
