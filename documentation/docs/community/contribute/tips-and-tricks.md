# Tips and tricks


This page provides useful snippets and how-tos while developing software for the PlanktoScope.

!!! warning

    This document is meant for PlanktoScope developers. Proceed with care.

- [Development OS](#development-os)
- [Development Environment](#development-environment)
- [Connect to router](#connect-to-router)
- [Disable splash screen](#disable-splash-screen)
- [Backup and Restore SD Card](#backup-and-restore-sd-card)
- [Documentation quick setup](#documentation-quick-setup)
- [Test dataset for segmenter](#test-dataset-for-segmenter)

## Development OS

On the Raspberry, we recommend using our developer image which is built upon [Raspberry Pi OS with desktop 64-bit](https://www.raspberrypi.com/software/operating-systems/#raspberry-pi-os-64-bit).

You can find the latest build in [actions](https://github.com/PlanktoScope/PlanktoScope/actions/workflows/build-os-bookworm-dx.yml?query=branch%3Amaster)

1. Choose the branch (e.g. `master`)
2. Click on the most recent action in the table
3. Download one of the Artifact depending on your PlanktoScope hardware
4. Run `unzip filename.zip` to extract files

See [Backup and Restore SD Card image](#backup-and-restore-sd-card) below to write the `.img.xz` file to the sdcard

## Development Environment

To setup the recommended development environment, run the following commands.

Make sure to replace `$planktoscope` with your PlanktoScope hostname, eg. `pkscope-sponge-bob-123`

<details>
    <summary>On the PlanktoScope</summary>

```sh
cd ~/PlanktoScope
# Enable Developer Mode
./software/distro/setup/planktoscope-app-env/PlanktoScope/enable-developer-mode
# Configure git
git config --global user.email "you@example.com"
git config --global user.name "Your Name"
```
</details>

<details>
    <summary>On your computer</summary>

```sh
# Create an SSH key for the PlanktoScope specifically
ssh-keygen -t ed25519 -C "pi@$planktoscope" -f ~/.ssh/$planktoscope
# Make the SSH key accepted by the PlanktoScope
ssh-copy-id -i ~/.ssh/$planktoscope.pub pi@$planktoscope
```

```
# Add the following to ~/.ssh/config
Host $planktoscope
  # https://docs.github.com/en/authentication/connecting-to-github-with-ssh/using-ssh-agent-forwarding
  ForwardAgent yes
  User pi
  IdentityFile ~/.ssh/planktoscope
```

</details>

---

You can now SSH into your PlanktoScope without username / password (using `ssh $planktoscope`) and use `~/PlanktoScope` as a regular git repository.

```sh
ssh $planktoscope
cd PlanktoScope
git status
git checkout master
```

We recommend developping directly from the PlanktoScope using [Visual Studio Code and the Remote - SSH extension](https://code.visualstudio.com/docs/remote/ssh).
Use `$planktoscope` as the host to connect to and open the "PlanktoScope" directory.

If you make changes to the backend, you can restart the backend and test your changes with

```sh
sudo systemctl restart planktoscope-org.device-backend.controller-planktoscopehat.service 
```

## Connect to router

The default behavior of the PlanktoScope is to act as a router to connect your computer to it directly via WiFi or Ethernet.

If you have a LAN it may be more convenient to connect the PlanktoScope to it and act as a simple client.

```sh
# Ethernet
nmcli connection down eth0-static
nmcli connection up eth0-default

# Wifi
nmcli connection down wlan0-hotspot
```

<details>
    <summary>Revert changes</summary>

```sh
# Ethernet
nmcli connection down eth0-default
nmcli connection up eth0-static

# Wifi
nmcli connection up wlan0-hotspot
```
</details>

Your PlanktoScope should be accessible via its hostname which you can retrieve from the PlanktoScope with `hostnamectl`

You can then ssh into it with `ssh://pi@pkscope-example-name-0000`

And access the UI with http://pkscope-example-name-0000/

If that doesn't work, type `nmap -sn 192.168.1.0/24` from your computer to find the PlanktoScope hostname and/or ip address.

See also the operating guide [Networking](https://docs-edge.planktoscope.community/operation/networking/)

## Disable splash screen

We recommend disabling the splash screen to get better boot logs

```sh
sudo nano /boot/firmware/cmdline.txt
# remove "quiet splash plymouth.ignore-serial-consoles"
```

## Backup and Restore SD Card

You will need to plug the SD card into your computer.

`/dev/device` refers to the path of the SD card device/disk. You will need to adjust it. Use `diskutil list` on macOS and `fdisk --list` on Linux.


```sh
# backup whole SD card onto an image file on your computer
sudo dd bs=1M if=/dev/device status=progress | xz > sdcard.img.xz
```

```sh
# restore an image file from your computer onto the SD card
xzcat sdcard.img.xz | sudo dd bs=1M of=/dev/device status=progress
```

See also the operating guide [SD Card Cloning](../../operation/clone-sd.md).

## Documentation quick setup

This is a quick setup guide. See also

* [documentation README](https://github.com/PlanktoScope/PlanktoScope/blob/master/documentation/README.md)
* [Writing Documentation](./documentation.md)

Install dependencies:

<details>
    <summary>Windows</summary>

Start by [installing WSL (Ubuntu)](https://learn.microsoft.com/en-us/windows/wsl/install#install-wsl-command)

Because of a small incompatibilty between Windows and Linux; we recommend cloning the repo "in WSL" but if you prefer keeping your git clone "in Windows", here are other options:
* [Git line endings](https://learn.microsoft.com/en-us/windows/wsl/tutorials/wsl-git#git-line-endings)
* [Visual Studio Code WSL extension](https://code.visualstudio.com/docs/remote/wsl)

Then follow the Ubuntu instructions below.
</details>

<details>
    <summary>Ubuntu</summary>

```shell
sudo apt update
sudo apt install python3-poetry
cd documentation
poetry install --no-root
```
</details>

<details>
    <summary>Fedora</summary>

```shell
sudo dnf install python3-poetry
cd documentation
poetry install --no-root
```
</details>

Run live previewer:

```sh
cd documentation
poetry run poe preview
```

Visit [`http://localhost:8000`](http://localhost:8000) to see local changes.

## Test dataset for segmenter

We have an
[example dataset](https://drive.google.com/drive/folders/1g6OPaUIhYkU2FPqtIK4AW6U4FYmhFxuw)
which you can use for testing the segmenter.

To use it, first download it as a `.zip` archive, e.g. to
`~/Downloads/BTS2023_S3_A2-TIMESTAMP-001.zip`. Then extract it:

```sh
unzip BTS2023_S3_A2-TIMESTAMP-001.zip
```

This will result in a new directory named `BTS2023_S3_A2`. Upload that new directory into the
PlanktoScope's `data/img` directory, e.g. via SCP:

```sh
scp -r BTS2023_S3_A2 pi@planktoscope.local:~/data/img
```

In the Node-RED dashboard's "Segmentation" page, press the "Update acquisition's folder list"
button. Then a new dataset named `BTS2023_S3_A2` should appear. If you run the segmenter on that
dataset, the segmenter should segment approximately 365 objects.
