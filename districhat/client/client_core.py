"""This module forms the clientside of the software. It's divided into two threads:
main thread for handling interaction with the user and another thread that handles
the communication with the server.
"""
import ipaddress
import json
import logging

from typing import Optional, Sequence, Tuple
from urllib import error, parse, request

import interface
from interface import MenuOptions

SERVER_PORT = 31683
TIMEOUT = 5.0

_logger = logging.getLogger("CLIENT")


def _chat_history(command_in: MenuOptions,
                  parameters_in: Sequence[str],
                  server_address: str):
    _logger.debug("Requesting chat history")

    if len(parameters_in) != 0:
        interface.invalid_parameter_count(command_in, parameters_in)
        return

    if server_address is None:
        interface.missing_server_address()
        return

    url = "http://" + server_address + ":" + str(SERVER_PORT) + "/chat-history"

    try:
        reply = request.urlopen(url, timeout=TIMEOUT).read()
    except error.URLError as e:
        _logger.warning("Unhandled exception in chat history: %s", e)
        reply = e.reason.encode("ascii")

    try:
        messages = json.loads(reply)
        interface.print_chat_log(messages)
    except json.decoder.JSONDecodeError:
        interface.unexpected_response(reply.decode("ascii"))


def _claim_nickname(command_in: MenuOptions,
                    parameters_in: Sequence[str],
                    server_address: str,
                    cookie_in: str) -> Tuple[Optional[str], Optional[str]]:
    _logger.debug("Claiming nickname")

    if len(parameters_in) != 1:
        interface.invalid_parameter_count(command_in, parameters_in)
        return None, None

    if server_address is None:
        interface.missing_server_address()
        return None, None

    nickname = parameters_in[0]
    cookie = None
    url = "http://" + server_address + ":" + str(SERVER_PORT) + "/claim-nick"

    try:
        contents = parse.urlencode({"nickname": nickname}).encode("ascii")
        headers = {}
        if cookie_in is not None:
            headers = {"cookie": cookie_in}
        req = request.Request(url, data=contents, headers=headers)
        reply = request.urlopen(req, timeout=TIMEOUT)
        reply_msg = reply.read().decode("ascii")
        cookie = reply.getheader("Set-Cookie").split("; ")[0].lstrip("cookie=")
    except error.URLError as e:
        # Logging & interface message work as expected so only need to set message
        _logger.warning("Unhandled exception in nickname claim: %s", e)
        reply_msg = e.reason

    if cookie is None:
        _logger.warning("No cookie provided or crash before reading cookie")
        interface.unexpected_response(reply_msg)
        return None, None
    interface.nickname_claimed(reply_msg)
    return cookie, nickname


def _help(command_in: MenuOptions, parameters_in: Sequence[str]):
    _logger.debug("Handling help")
    command_help = None
    if len(parameters_in) not in [0, 1]:
        interface.invalid_parameter_count(command_in, parameters_in)
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
        reply_msg = request.urlopen(url, timeout=TIMEOUT).read().decode("ascii")
    except error.URLError as e:
        # Logging & interface message work as expected so only need to set message
        reply_msg = e

    if reply_msg == "pongers\n":
        # Server responded as expected
        _logger.info("Server at {} responded accordingly.".format(server_ip))
        return True
    _logger.info("The server {} responded unexpectedly: {}".format(server_ip,
                                                                   reply_msg))
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
    cookie = None
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
            cookie, nickname = _claim_nickname(command_in,
                                               parameters_in,
                                               server_address,
                                               cookie)

        elif command_in == MenuOptions.JOIN_SERVER:
            # _join_server(command_in, parameters_in)
            pass

        elif command_in == MenuOptions.SEND_MESSAGE:
            _send_message(command_in, parameters_in, server_address, cookie)
            pass

        elif command_in == MenuOptions.HELP:
            _help(command_in, parameters_in)
    interface.exit_application()


def _send_message(command_in: MenuOptions,
                  parameters_in: Sequence[str],
                  server_address: str,
                  cookie_in: str):
    _logger.debug("Sending message")
    if len(parameters_in) == 0:
        interface.invalid_parameter_count(command_in, parameters_in)
        return

    if server_address is None:
        interface.missing_server_address()
        return

    if cookie_in is None:
        interface.missing_nickname()
        return

    message = " ".join(parameters_in)
    cookie = None
    url = "http://" + server_address + ":" + str(SERVER_PORT) + "/send-message"

    try:
        contents = parse.urlencode({"message": message}).encode("ascii")
        headers = {}
        if cookie_in is not None:
            headers = {"cookie": cookie_in}
        req = request.Request(url, data=contents, headers=headers)
        reply = request.urlopen(req, timeout=TIMEOUT)
        reply_msg = reply.read().decode("ascii")
        cookie = reply.getheader("Set-Cookie").split("; ")[0].lstrip("cookie=")
    except error.URLError as e:
        # Logging & interface message work as expected so only need to set message
        _logger.warning("Unhandled exception in message sending: %s", e)
        reply_msg = e.reason

    if cookie is None:
        _logger.warning("No cookie provided or crash before reading cookie")
        interface.unexpected_response(reply_msg)
        return
    interface.message_sent(reply_msg)
    return


def _set_server(command_in: MenuOptions, parameters_in: Sequence[str]) -> Optional[str]:
    _logger.debug("Setting server address")
    if len(parameters_in) != 1:
        interface.invalid_parameter_count(command_in, parameters_in)
        return None
    server_ip = parameters_in[0]
    try:
        ipaddress.ip_address(server_ip)
    except ValueError:
        interface.invalid_ip_address(server_ip)
        return None
    if _ping_server(server_ip):
        _logger.info("Set server address to {}".format(server_ip))
        return server_ip


if __name__ == "__main__":
    run()
