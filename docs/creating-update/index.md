# Creating a new update

Since PlanktoScope OS v2026, we use [RAUC](https://rauc.readthedocs.io/) to create and install software updates.

The PlanktoScope contains 2 slots; A and B; each able to host the entirety of the operating system.

To create an update

```sh
# Install pkos
just -f /opt/PlanktoScope/os/pkos/justfile

# Install RPI OS rauc bundle to slot B (see Updating Raspberry Pi OS to create a rauc bundle)
rauc install PlanktoScopeOS-2026-06-18-raspios.raucb

# Boot to slot B
sudo pkos reboot B

# Install deps
sudo apt install git just
git clone https://github.com/fairscope/PlanktoScope.git
sudo mv PlanktoScope /opt/PlanktoScope
sudo chown -R pi:pi /opt/PlanktoScope

# Install pkos
just -f /opt/PlanktoScope/os/pkos/justfile

# Run setup scripts
sudo pkos prepare

# Boot to slot A
sudo pkos reboot A

# Create bundle
sudo pkos create-bundle /dev/nvme0n1 B 2026.4.0
```

You can swap A and B.
