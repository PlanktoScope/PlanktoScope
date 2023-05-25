# Maintenance and Repair

Instructions for maintaining and repairing an open-source hardware microscope.

## Cleaning the optics

* Begin by turning off the microscope and unplugging it from any power source.
Gently remove any dust or debris using a soft, dry cloth.
* To clean the lenses and other optics, use a lens cleaning solution and a lens cleaning tissue or cloth. Gently wipe the optics in a circular motion, starting from the center and working outward. Avoid applying too much pressure or using a rough cloth, as this can scratch or damage the optics.
* Once you have finished cleaning the optics, use a dry cloth to remove any excess moisture or cleaning solution.

## The Linear Bearings

Linear bearings are mechanical components that allow for smooth, precise linear movement along a shaft or track. Proper inspection and maintenance of linear bearings is essential for ensuring their optimal performance and longevity. In this tutorial, we will discuss how to inspect and maintain linear bearings, including checking for visual and noise issues during operation, cleaning, and lubrication.

### Inspection

Linear bearings should be inspected regularly to ensure that they are functioning properly and are in good condition. There are several key aspects to consider during an inspection:

1. Visual inspection: Look for any visible signs of damage or wear, such as cracks, chips, or deformities in the bearing surfaces or seals.
2. Noise during operation: Listen for any unusual noises or vibrations while the bearing is in use. These may indicate a problem with the bearing or the surrounding machinery.
3. Movement: Check the smoothness and accuracy of the bearing's movement along the shaft or track. Any roughness or deviation from a straight path may indicate a problem with the bearing or the surrounding machinery.

### Maintenance

There are several steps you can take to maintain linear bearings and ensure their optimal performance:

1. Cleaning: Linear bearings should be kept clean to prevent debris from entering and damaging the bearings. Use a clean, dry cloth to wipe away any dirt or debris from the bearing surfaces and seals.
2. Lubrication: Proper lubrication is essential for the smooth operation of linear bearings. Use a high-quality lubricant specifically designed for linear bearings, and follow the manufacturer's recommendations for the frequency and amount of lubrication.
3. Replacement: If a linear bearing is damaged or excessively worn, it should be replaced to ensure the smooth and accurate operation of the machinery.

### Conclusion

Proper inspection and maintenance of linear bearings is essential for ensuring their optimal performance and longevity. By regularly inspecting the bearings for visual and noise issues, and maintaining them through cleaning and lubrication, you can help ensure that your machinery operates smoothly and efficiently.

## The operating system

Tutorial for maintaining and repairing a Debian-based operating system:

1. Connecting to the device:
   * To connect to the device, you will need to use a terminal emulator such as PuTTY or GNOME Terminal.
   * You will need to know the IP address or hostname of the device, as well as the username and password for an account with admin privileges.
   * Once you have entered this information, click "Connect" to establish a connection to the device.
2. System upgrade:
   * Once you are connected to the device, enter the command `sudo apt update` to retrieve a list of available software updates.
   * Then, enter the command `sudo apt upgrade` to download and install the available updates.
   * Wait for the update process to complete, and then restart the system to apply the changes.
3. Analysis of log files with journald:
   * Journald is a system service that manages and stores log files on a Debian-based system.
   * To view the log files using journald, enter the command `journalctl` in the terminal. This will show the log entries in chronological order.
   * You can use the options "--since" and "--until" to specify a time range for the log entries. For example, `journalctl --since yesterday` will show the log entries from the past 24 hours.
   * `journalctl -p 3 -xb` will show all log entries that contain the word "error".
4. Available disk space:
   * To check the available disk space on the system, enter the command `df -h`. This will show the available space on each disk partition.
   * If the available space is low, you can use the command `sudo apt autoremove` to remove unnecessary software packages, or the command `sudo apt clean` to delete temporary files.
5. Service monitoring using systemctl:
   * To view the services running on the system, enter the command `systemctl list-units`. This will show a list of all running services.
   * To check failed status of all service, use the command `systemctl list-units --failed`.
