#!/bin/bash

# This work is licensed under the Unlicense

# This script is based on https://serverfault.com/a/767079 posted
# by Mike Blackwell, modified to our needs. Credits to the author.

# This script is called from systemd unit file to mount or unmount
# a USB drive.

PATH="$PATH:/usr/bin:/usr/local/bin:/usr/sbin:/usr/local/sbin:/bin:/sbin"
log="echo "

usage()
{
    ${log} "Usage: $0 device_path (e.g. /dev/sdb1)"
    exit 1
}

if [[ $# -ne 1 ]]; then
    usage
fi

DEVICE=$1
DEVBASE=$(echo "${DEVICE}" | cut -d'/' -f 3)
SOURCE="/home/pi/data/" # source of files

# See if this drive is already mounted, and if so where
MOUNT_POINT=$(mount | grep "${DEVICE}" | awk '{ print $3 }')

DEV_LABEL=""

do_mount()
{
    if [[ -n ${MOUNT_POINT} ]]; then
        ${log} "Warning: ${DEVICE} is already mounted at ${MOUNT_POINT}"
        exit 2
    fi

    # Get info for this drive: $ID_FS_LABEL and $ID_FS_TYPE
    eval '$(blkid -o udev "${DEVICE}" | grep -i -e "ID_FS_LABEL" -e "ID_FS_TYPE")'

    # Figure out a mount point to use
    LABEL=${ID_FS_LABEL}
    if grep -q " /media/${LABEL} " /etc/mtab; then
        # Already in use, make a unique one
        LABEL+="-${DEVBASE}"
    fi
    DEV_LABEL="${LABEL}"

    # Use the device name in case the drive doesn't have label
    if [ -z "${DEV_LABEL}" ]; then
        DEV_LABEL="${DEVBASE}"
    fi

    MOUNT_POINT="/media/${DEV_LABEL}"

    ${log} "Mount point: ${MOUNT_POINT}"

    mkdir -p "${MOUNT_POINT}"

    # Global mount options
    OPTS="rw,relatime"

    # File system type specific mount options
    if [[ ${ID_FS_TYPE} == "vfat" ]]; then
        OPTS+=",users,gid=100,umask=000,shortname=mixed,utf8=1,flush"
    fi

    if ! mount -o ${OPTS} "${DEVICE}" "${MOUNT_POINT}"; then
        ${log} "Error mounting ${DEVICE} (status = $?)"
        rmdir "${MOUNT_POINT}"
        exit 3
    else
        # Track the mounted drives
        echo "${MOUNT_POINT}:${DEVBASE}" | cat >> "/var/log/usb-mount.track"
    fi

    ${log} "Mounted ${DEVICE} at ${MOUNT_POINT}"
}

do_unmount()
{
    if [[ -z ${MOUNT_POINT} ]]; then
        ${log} "Warning: ${DEVICE} is not mounted"
    else
        umount -l "${DEVICE}"
	    ${log} "Unmounted ${DEVICE} from ${MOUNT_POINT}"
        /bin/rmdir "${MOUNT_POINT}"
        sed -i.bak "\@${MOUNT_POINT}@d" /var/log/usb-mount.track
    fi


}

do_backup()
{
    do_mount
    if [[ -z ${MOUNT_POINT} ]]; then
        ${log} "Warning: ${DEVICE} is not mounted"
    else
        ${log} "Starting to backup the local files"
        MACHINE=$(python3 -c "import planktoscope.uuidName as uuidName; print(uuidName.machineName(machine=uuidName.getSerial()).replace(' ','_'))")
        BACKUP_FOLDER="${MOUNT_POINT}/planktoscope_data/${MACHINE}"
        ${log} "Machine name is ${MACHINE}, backup folder is ${BACKUP_FOLDER}"
        mkdir -p "$BACKUP_FOLDER"
        rsync -rtD --modify-window=1 --update -W --inplace  "$SOURCE" "$BACKUP_FOLDER"
        ${log} "Main copy done, checking integrity now"
        if ! python3 -m planktoscope.integrity -c "$BACKUP_FOLDER"; then
            ${log} "ERROR: Some files were corrupted during the copy!"
            do_unmount
            exit 4
        else
            ${log} "All files copied successfully!"
        fi
        do_unmount
    fi
}


do_backup
