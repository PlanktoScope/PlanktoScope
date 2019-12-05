=============
Remote access
=============

This tutorial is allowing your Raspberry Pi 

.. warning::

    Make sure your Raspberry Pi is connected to Internet either via WiFi or Ethernet.
    
    
Use the command lines to first update and upgrade your Raspbian ::

    $ sudo apt-get update -y
    $ sudo apt-get dist-upgrade -y
    
It's a good practice to reboot after that using ::

    $ sudo reboot now

Install all the required packages this command ::

    $ sudo apt-get install dnsmasq hostapd -y
    
   
.. _test_suite:

Test suite
==========

If you wish to run the picamera test suite, follow the instructions in
:ref:`dev_install` above and then make the "test" target within the sandbox::

    $ source sandbox/bin/activate
    (sandbox) $ cd picamera
    (sandbox) $ make test

.. warning::

    The test suite takes a *very* long time to execute (at least 1 hour on an
    overclocked Pi 3). Depending on configuration, it can also lockup the
    camera requiring a reboot to reset, so ensure you are familiar with SSH or
    using alternate TTYs to access a command line in the event you need to
    reboot.

