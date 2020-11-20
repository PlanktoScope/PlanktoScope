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


def get_checksum(filename):
    """returns the sha1 checksum of the file

    Args:
        filename (string): file name of the file to calculate the checksum of

    Returns:
        string: sha1 checksum of the file
    """
    logger.debug(f"Calculating the integrity of {filename}'s content")
    if not os.path.exists(filename):
        # The file does not exists!
        logger.error(f"The file {filename} does not exists!")
        raise FileNotFoundError

    # since we are just doing integrity verification, we can use an "insecure" hashing algorithm. If it's good for git, it's good for us.
    sha1 = hashlib.sha1()  # nosec
    with open(filename, "rb") as f:
        while True:
            # Let's read chunks in the algorithm block size we use
            chunk = f.read(sha1.block_size)
            if not chunk:
                break
            sha1.update(chunk)

    return sha1.hexdigest()


def get_filename_checksum(filename):
    """returns the sha1 checksum of the filename, a null character and the data

    Args:
        filename (string): file name of the file to calculate the checksum of

    Returns:
        string: sha1 checksum of the filename and its content
    """
    logger.debug(f"Calculating the integrity of {filename}'s content and its filename")
    if not os.path.exists(filename):
        # The file does not exists!
        logger.error(f"The file {filename} does not exists!")
        raise FileNotFoundError

    # since we are just doing integrity verification, we can use an "insecure" hashing algorithm. If it's good for git, it's good for us.
    sha1 = hashlib.sha1()  # nosec
    sha1.update(os.path.split(filename)[1].encode())
    sha1.update("\00".encode())
    with open(filename, "rb") as f:
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

    integrity_file_path = os.path.join(path, "integrity.check")
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
        logger.error(f"The file {filename} does not exists!")
        raise FileNotFoundError

    integrity_file_path = os.path.join(os.path.dirname(filepath), "integrity.check")
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


def check_path_integrity(path):
    # TODO implement the method that recursively reads the integrity file of a repository and checks everything down to the file
    pass


if __name__ == "__main__":
    # TODO add here a way to check a folder integrity easily with a simple command line
    # something like python3 scripts/planktoscope/integrity.py -c path/to/folder/to/check
    pass