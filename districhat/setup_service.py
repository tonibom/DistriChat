"""This python script is run on the serverside when the server boots up.
This script clones the GitHub repository and runs the server_setup.py script
from within the repository.
"""
import logging
import os
import subprocess


SERVER_PATH = "/home/tonibom"
REPOSITORY = "git@github.com:tonibom/DistriChat.git"

_logger = logging.getLogger("DC-INSTALLER")


def main():
    logging.basicConfig(level=logging.DEBUG)

    os.chdir(SERVER_PATH)

    _logger.debug("Cloning repository {}...".format(REPOSITORY))
    call = ["git", "clone", REPOSITORY]
    subprocess.run(call, check=True)
    _logger.debug("Successfully cloned repository.")

    os.chdir(SERVER_PATH + "/DistriChat")

    _logger.debug("Running server_setup.py")
    call = ["python3", "server_setup.py"]
    subprocess.run(call, check=True)
    _logger.debug("Started server_setup.py")


if __name__ == "__main__":
    main()
