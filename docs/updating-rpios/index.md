# Updating Raspberry Pi OS

Since PlanktoScope OS v2026, we use [RAUC](https://rauc.readthedocs.io/) to create and install software updates.

The PlanktoScope contains 2 slots; A and B; each able to host the entirety of the operating system.

To create a matching rauc bundle

```sh
# Install pkos
just -f /opt/PlanktoScope/os/pkos/justfile

# Boot to slot A
sudo pkos reboot A

# Update /opt/PlanktoScope/os/RPIOS.env if wanted

# Install RPIOS and create bundle
sudo NODE_EXECA=debug pkos create-rpios-bundle /dev/nvme0n1 B

# It will display the path of the raucb file
# On your computer download the file
scp planktoscope-sponge-bob:/data/tmp/PlanktoScopeOS-rpios-yyyy-mm-dd.raucb .

# Install the bundle to make sure it is working as expected
rauc install /data/tmp/PlanktoScopeOS-rpios-yyyy-mm-dd.raucb

# Reboot into the new active slot for testing
sudo reboot
```

You can also swap A and B.
