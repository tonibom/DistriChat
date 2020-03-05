"""This setup script is used by the server upon startup to setup the serverside.
"""
import logging
import os
import subprocess

SERVER_DIR = "/home/tonibom/DistriChat"
SERVICE_FILE = "/services/districhat.service"
SYSTEMD_SERVICE_LOCATION = "/etc/systemd/system/"

_logger = logging.getLogger("SERVER-SETUP")


def main():

    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s:%(levelname)s: %(message)s")
    _logger.info("Starting up...")
    os.chdir(SERVER_DIR)

    call = ["sudo", "mv", SERVER_DIR + SERVICE_FILE, SYSTEMD_SERVICE_LOCATION]
    subprocess.run(call, check=True)
    _logger.info("Added the service file to services.")

    call = ["sudo", "systemctl", "daemon-reload"]
    subprocess.run(call, check=True)
    _logger.info("Reloaded systemctl daemon.")

    call = ["sudo", "systemctl", "start", "districhat.service"]
    subprocess.run(call, check=True)
    _logger.info("Started up districhat.service")

    _logger.info("Finished server setup")


if __name__ == "__main__":
    main()
