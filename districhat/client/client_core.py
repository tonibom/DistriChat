"""This module forms the clientside of the software. It's divided into two threads:
main thread for handling interaction with the user and another thread that handles
the communication with the server.
"""
import ipaddress
import json
import logging
import urllib.error
import urllib.request

from typing import Optional, Sequence

import interface
from interface import MenuOptions

_logger = logging.getLogger("CLIENT")
SERVER_PORT = 5000


def _chat_history(command_in: MenuOptions,
                  parameters_in: Sequence[str],
                  server_address: str):
    _logger.debug("Requesting chat history")

    if len(parameters_in) != 0:
        interface.invalid_parameter_count(command_in,
                                          parameters_in)
        return

    if server_address is None:
        interface.missing_server_address()
        return

    url = "http://" + server_address + ":" + str(SERVER_PORT) + "/chat-history"
    reply = urllib.request.urlopen(url, timeout=5.0).read()
    try:
        messages = json.loads(reply)
        interface.print_chat_log(messages)
    except json.decoder.JSONDecodeError:
        interface.unexpected_response(reply)


def _help(command_in: MenuOptions, parameters_in: Sequence[str]):
    _logger.debug("Handling help")
    command_help = None
    if len(parameters_in) not in [0, 1]:
        interface.invalid_parameter_count(command_in,
                                          parameters_in)
        return
    if len(parameters_in) == 1:
        try:
            command_help = interface.MENU_COMMANDS[parameters_in[0].upper()]
        except KeyError:
            interface.invalid_command_for_help(parameters_in[0])
            return
    interface.print_help(command_help)


def _ping_server(server_ip: str) -> bool:
    _logger.debug("Pinging server")
    url = "http://" + server_ip + ":" + str(SERVER_PORT) + "/ping"
    try:
        reply = urllib.request.urlopen(url, timeout=5.0).read().decode("ascii")
    except urllib.error.URLError:
        # Logging & interface message work as expected so only need to set message
        reply = "Connection refused"

    if reply == "pongers\n":
        # Server responded as expected
        _logger.info("Server at {} responded accordingly.".format(server_ip))
        return True
    _logger.info("The server {} responded unexpectedly: {}".format(server_ip,
                                                                   reply))
    interface.invalid_server_address(server_ip)
    return False


def run():
    """Try for modular structure:
    Open interface's main menu
    Use the result to close / open up the selected menu
    """
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s:%(levelname)s: %(message)s")

    # TODO: Check local storage for nickname & cookie and server address
    nickname = None
    server_address = None

    interface.welcome()

    command_in = None

    while command_in != MenuOptions.QUIT:
        # Take the input from the user
        command_in, parameters_in = interface.main_menu()
        _logger.debug("User inputted command %s with parameters %s",
                      command_in,
                      parameters_in)

        if command_in == MenuOptions.SERVER:
            server_address = _set_server(command_in, parameters_in)

        elif command_in == MenuOptions.CHAT_HISTORY:
            _chat_history(command_in, parameters_in, server_address)

        elif command_in == MenuOptions.CLAIM_NICKNAME:
            # _claim_nickname(command_in, parameters_in)
            pass

        elif command_in == MenuOptions.JOIN_SERVER:
            # _join_server(command_in, parameters_in)
            pass

        elif command_in == MenuOptions.SEND_MESSAGE:
            # _send_message(command_in, parameters_in)
            pass

        elif command_in == MenuOptions.HELP:
            _help(command_in, parameters_in)
    interface.exit_application()


def _set_server(command_in: MenuOptions, parameters_in: Sequence[str]) -> Optional[str]:
    _logger.debug("Setting server address")
    if len(parameters_in) != 1:
        interface.invalid_parameter_count(command_in,
                                          parameters_in)
        return
    server_ip = parameters_in[0]
    try:
        ipaddress.ip_address(server_ip)
    except ValueError:
        interface.invalid_ip_address(server_ip)
        return
    if _ping_server(server_ip):
        _logger.info("Set server address to {}".format(server_ip))
        return server_ip


if __name__ == "__main__":
    run()
