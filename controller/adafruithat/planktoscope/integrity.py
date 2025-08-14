# Copyright (C) 2021 Romain Bazile
#
# This file is part of the PlanktoScope software.
#
# PlanktoScope is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PlanktoScope is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PlanktoScope.  If not, see <http://www.gnu.org/licenses/>.

# This module calculates the checksum of created files and add them to and file called integrity.check
# The file is composed as follows:
# First, a header that starts by like so:
#           # planktoscope integrity file, see https://www.planktoscope.org
#           # filename,size,sha1
# The second line define the order of the informations are saved in, for now, it's all locked down
# The following lines exists one per file, with the name of the file, its size in bytes and its sha1 checksum


import os
import hashlib

# Logger library compatible with multiprocessing
from loguru import logger

integrity_file_name = "integrity.check"


def get_checksum(filepath):
    """returns the sha1 checksum of the file

    Args:
        filepath (string): file name of the file to calculate the checksum of

    Returns:
        string: sha1 checksum of the file
    """
    logger.debug(f"Calculating the integrity of {filepath}'s content")
    if not os.path.exists(filepath):
        # The file does not exists!
        logger.error(f"The file {filepath} does not exists!")
        raise FileNotFoundError

    # since we are just doing integrity verification, we can use an "insecure" hashing algorithm. If it's good for git, it's good for us.
    sha1 = hashlib.sha1()  # nosec
    with open(filepath, "rb") as f:
        while True:
            # Let's read chunks in the algorithm block size we use
            chunk = f.read(sha1.block_size)
            if not chunk:
                break
            sha1.update(chunk)

    return sha1.hexdigest()


def get_filename_checksum(filepath):
    """returns the sha1 checksum of the filename, a null character and the data

    Args:
        filepath (string): file name of the file to calculate the checksum of

    Returns:
        string: sha1 checksum of the filename and its content
    """
    logger.debug(f"Calculating the integrity of {filepath}'s content and its filename")
    if not os.path.exists(filepath):
        # The file does not exists!
        logger.error(f"The file {filepath} does not exists!")
        raise FileNotFoundError

    # since we are just doing integrity verification, we can use an "insecure" hashing algorithm. If it's good for git, it's good for us.
    sha1 = hashlib.sha1()  # nosec
    sha1.update(os.path.split(filepath)[1].encode())
    sha1.update("\00".encode())
    with open(filepath, "rb") as f:
        while True:
            # Let's read chunks in the algorithm block size we use
            chunk = f.read(sha1.block_size)
            if not chunk:
                break
            sha1.update(chunk)

    return sha1.hexdigest()


def create_integrity_file(path):
    """Create an integrity file in the designated path

    Args:
        path (string): path where to create the integrity file

    Raises:
        FileExistsError: Raised if the integrity file already exists there.
    """
    logger.debug(f"Create the integrity file in the folder {path}")
    # check if the path already exists
    if not os.path.exists(path):
        # make sure the directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)

    integrity_file_path = os.path.join(path, integrity_file_name)
    if os.path.exists(integrity_file_path):
        logger.error(f"The integrity file already exists in the folder {path}")
        # The file already exists!
        raise FileExistsError

    # create the file
    with open(integrity_file_path, "w") as file:
        file.write("# planktoscope integrity file, see https://www.planktoscope.org\n")
        file.write("# filename,size,sha1\n")


def append_to_integrity_file(filepath):
    """Append the information about a filename to the integrity file in its folder

    Args:
        filepath (string): path of the file to add to the integrity file
    """
    # Append to the integrity file the specific file
    if not os.path.exists(filepath):
        logger.error(f"The file at {filepath} does not exists!")
        raise FileNotFoundError

    integrity_file_path = os.path.join(os.path.dirname(filepath), integrity_file_name)
    # Check that the integrity files exists
    if not os.path.exists(integrity_file_path):
        logger.debug(f"The integrity file does not exists in the folder of {filepath}")
        create_integrity_file(os.path.dirname(filepath))

    with open(integrity_file_path, "a") as file:
        file.write(
            f"{os.path.split(filepath)[1]},{os.path.getsize(filepath)},{get_filename_checksum(filepath)}\n"
        )


def scan_path_to_integrity(path):
    # TODO implement the method that add all files in the folder to the integrity file
    pass


def check_integrity(path):
    valid = []
    not_valid = []
    integrity_file_path = os.path.join(path, integrity_file_name)

    with open(integrity_file_path, "r") as integrity_file:
        if integrity_file.readline().startswith("#") and integrity_file.readline().startswith("#"):
            for line in integrity_file:
                filename, size, checksum = line.rstrip().split(",")
                filepath = os.path.join(path, filename)
                actual_checksum = get_filename_checksum(filepath)
                actual_size = os.path.getsize(filepath)
                if actual_checksum == checksum and actual_size == int(size):
                    valid.append(filename)
                else:
                    print(
                        f"{filename} with checksum {actual_checksum} vs {checksum} and size {actual_size} vs {size} is not valid"
                    )
                    not_valid.append(filename)
        else:
            print(f"The integrity file at {integrity_file_path} is not valid")
    return (valid, not_valid)


def check_path_integrity(path):
    # TODO implement the method that recursively reads the integrity file of a repository and checks everything down to the file
    # Recursively scan all directories and save the ones with an integrity file in them
    to_scan = [root for root, dirs, files in os.walk(path) if integrity_file_name in files]

    valid_list = []
    not_valid_list = []
    for folder in to_scan:
        valid, not_valid = check_integrity(folder)
        valid_list += valid
        not_valid_list += not_valid
    if not_valid_list:
        print(
            f"{len(not_valid_list)} inconsistent file(s) have been found, please check them manually"
        )
        print(not_valid_list)
        return 1
    return 0


if __name__ == "__main__":
    import sys

    logger.remove()

    if len(sys.argv) > 2:
        # let's check them arguments
        if sys.argv[1] != "-c":
            print(
                "To check the integrity of files in a given folder, please use python3 -m planktoscope.integrity -c /path/to/folder"
            )
            exit(0)
        else:
            path_to_check = sys.argv[2]
            # let's check if the path exists
            if not os.path.exists(path_to_check):
                print("The path to check doesn't exists")
                exit(1)

            # the path exists, let's check it!
            error = check_path_integrity(path_to_check)
            if error:
                exit(error)
            print("All the files are valid")

    exit(0)
