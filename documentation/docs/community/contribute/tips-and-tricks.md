# Tips and tricks

This page provides useful snippets and how-tos while developing software for the PlanktoScope.

!!! warning

    This document is meant for PlanktoScope developers. Proceed with care.

## Building the OS

### Install Raspberry Pi OS

Download [2025-05-13-raspios-bookworm-arm64-lite.img.xz](https://downloads.raspberrypi.com/raspios_lite_arm64/images/raspios_lite_arm64-2025-05-13/).

Use [Raspberry Pi Imager](https://www.raspberrypi.com/software/) and select **Use custom** to pick the downloaded `.img.xz` file.

When asked to **Use OS customization?** press **EDIT SETTINGS**

* Set **Username** to `pi`
* Set **Password** to `copepode`
* Enable SSH with `Use password authentication`

Boot into Raspberry Pi OS and type the following commands using SSH

```sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/PlanktoScope/PlanktoScope/HEAD/os/setup.sh)"
# After the script ran succesfully
sudo systemctl reboot
```

After the PlanktoScope has rebooted you can open its URL in your browser.

PlanktoScope OS is ready.

## Updating the OS

Type the following commands

```sh
cd /home/pi/PlanktoScope
git checkout main
git pull
just
# After the script ran succesfully
sudo systemctl reboot
```

PlanktoScope OS is updated.

## Graphical UI

To install the graphical desktop similar to what you find on the desktop edition of Raspberry Pi OS proceed as following:

```sh
sudo apt install raspberrypi-ui-mods
# Change the boot option
sudo raspi-config # System Options -> Boot -> Desktop GUI
sudo systemctl reboot
```

## Development Environment

To setup the recommended development environment, run the following commands.

Make sure to replace `$planktoscope` with your PlanktoScope hostname, eg. `pkscope-sponge-bob-123`

<details>
    <summary>On your computer</summary>

```sh
# Create an SSH key for the PlanktoScope specifically
ssh-keygen -t ed25519 -C "pi@$planktoscope" -f ~/.ssh/$planktoscope
# Make the SSH key accepted by the PlanktoScope
ssh-copy-id -i ~/.ssh/$planktoscope.pub pi@$planktoscope
# Add your keys to your SSH agent
ssh-add -k
```

```sh
# Add the following to ~/.ssh/config
Host $planktoscope
  # https://docs.github.com/en/authentication/connecting-to-github-with-ssh/using-ssh-agent-forwarding
  ForwardAgent yes
  User pi
  IdentityFile ~/.ssh/$planktoscope
```

</details>

You can now SSH into your PlanktoScope without username / password (using `ssh $planktoscope`).

<details>
    <summary>On the PlanktoScope</summary>

```sh
cd ~/PlanktoScope
just developer-mode
git checkout main
git status
```

</details>

We recommend developping directly from the PlanktoScope using [Visual Studio Code and the Remote - SSH extension](https://code.visualstudio.com/docs/remote/ssh) or [Zed - Remote Development](https://zed.dev/docs/remote-development). Use `$planktoscope` as the host to connect to and open the `/home/pi/PlanktoScope` directory.

## Connect to router

The supported way to connect the PlanktoScope to a router is with an Ethernet cable.
If that is not possible you may try the following:

```sh
nmcli connection down wlan0-hotspot
nmcli device wifi list
nmcli device wifi connect "<SSID>" --ask
```

Your PlanktoScope should be accessible via its hostname which you can retrieve from the PlanktoScope with `hostnamectl`

You can then ssh into it with `ssh://pi@pkscope-example-name-0000`

And access the UI with http://pkscope-example-name-0000/

If that doesn't work, type `nmap -sn 192.168.1.0/24` from your computer to find the PlanktoScope hostname and/or ip address.

## Offline access

When network is not available you have several options for debugging

- Plug-in a keyboard and display (needs micro HDMI adapter)
- [Connect a serial cable](https://www.jeffgeerling.com/blog/2021/attaching-raspberry-pis-serial-console-uart-debugging)
- Use [NanoKVM USB](https://wiki.sipeed.com/hardware/en/kvm/NanoKVM_USB/introduction.html) (no need for network)
- Use [JetKVM](https://jetkvm.com/) (local network needed)

## Backup and Restore SD Card

Plug the SD card into your computer.

`/dev/device` refers to the path of the SD card device/disk. You will need to adjust it. Use `diskutil list` on macOS and `fdisk --list` on Linux.

```sh
# backup whole SD card onto an image file on your computer
sudo dd bs=1M if=/dev/device status=progress conv=fdatasync | xz > sdcard.img.xz
```

```sh
# restore an image file from your computer onto the SD card
xzcat sdcard.img.xz | sudo dd bs=1M of=/dev/device status=progress conv=fdatasync
```

See also the operating guide [SD Card Cloning](../../operation/clone-sd.md).

## Opening a port on the firewall

https://firewalld.org/documentation/howto/open-a-port-or-service.html

## Working with GPIOs on the CLI

https://lloydrochester.com/post/hardware/libgpiod-intro-rpi/

## Documentation quick setup

This is a quick setup guide. See also

- [documentation README](https://github.com/PlanktoScope/PlanktoScope/blob/main/documentation/README.md)
- [Writing Documentation](./documentation.md)

Install dependencies:

<details>
    <summary>Windows</summary>

Start by [installing WSL (Ubuntu)](https://learn.microsoft.com/en-us/windows/wsl/install#install-wsl-command)

Because of a small incompatibilty between Windows and Linux; we recommend cloning the repo "in WSL" but if you prefer keeping your git clone "in Windows", here are other options:

- [Git line endings](https://learn.microsoft.com/en-us/windows/wsl/tutorials/wsl-git#git-line-endings)
- [Visual Studio Code WSL extension](https://code.visualstudio.com/docs/remote/wsl)

Then follow the Ubuntu instructions below.

</details>

<details>
    <summary>Ubuntu</summary>

```shell
sudo apt update
sudo apt install python3-poetry
cd documentation
poetry install
```

</details>

<details>
    <summary>Fedora</summary>

```shell
sudo dnf install python3-poetry
cd documentation
poetry install
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
