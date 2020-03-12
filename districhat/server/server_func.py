"""The server functions collection as a separate module so that the handler for
the web requests can be implemented separately. This modular separation allows
for changing to using different frameworks for the actual server request handler
implementation whilst keeping the server functionality intact.
"""
import datetime
import logging
import random
import string

from typing import Sequence, Tuple

import zmq

# TODO: Placeholder
ACCOUNTS = {}
COOKIE_LENGTH = 128
EPOCH = datetime.datetime(1970, 1, 1)
ZMQ_BIND_ADDRESS = "tcp://0.0.0.0"

_logger = logging.getLogger("SERVER-FUNCTIONS")


class AccountNotFoundException(Exception):
    pass


class Message:
    def __init__(self, timestamp: float, nickname: str, message_str: str):
        self.timestamp = timestamp
        self.sender = nickname
        self.message = message_str

    def formatted(self) -> str:
        time_str = datetime.datetime.fromtimestamp(self.timestamp).isoformat()
        return " -- ".join([time_str, self.sender, self.message])


class MessageQueue:
    def __init__(self):
        self.messages = []

    def add_message(self, message: Message):
        self.messages.append(message)

    def get_messages_formatted(self) -> Sequence[str]:
        formatted_messages = [msg.formatted() for msg in self.messages]
        return formatted_messages


def claim_nickname(nickname: str, cookie: str) -> str:
    if cookie in ACCOUNTS.keys() and nickname == ACCOUNTS[cookie]:
        # Nickname exists and the user provided the corresponding cookie
        _logger.debug("Nickname {} existed for {}.".format(nickname, cookie))
        _logger.debug("{} == {}".format(nickname, ACCOUNTS[cookie]))
        response_msg = "Nickname {} is registered to you".format(nickname)

    elif nickname not in ACCOUNTS.values():
        # Nickname is available
        if cookie in ACCOUNTS.keys():
            # User already has a registered nickname
            old_nickname = ACCOUNTS[cookie]
            _logger.info("User {} already had the nickname {}. Replacing the nickname with {}.".format(
                         cookie, old_nickname, nickname))
            ACCOUNTS.pop(cookie)
            ACCOUNTS[cookie] = nickname
            response_msg = "Replaced nickname {} with {}".format(old_nickname, nickname)
        else:
            ACCOUNTS[cookie] = nickname
            _logger.debug("Nickname {} claimed for {}.".format(nickname, cookie))
            response_msg = "Claimed nickname {}".format(nickname)
    else:
        response_msg = "Nickname {} is already in use. Try another one.".format(nickname)
    return response_msg


def create_publish_socket() -> Tuple[zmq.Socket, int]:
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    port = socket.bind_to_random_port(ZMQ_BIND_ADDRESS, min_port=49152, max_port=65536, max_tries=100)
    _logger.info("Created a ZMQ PUB TCP socket on port %s", port)
    return socket, port


def generate_cookie() -> str:
    while True:
        cookie = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(COOKIE_LENGTH)])
        if cookie not in ACCOUNTS.keys():
            # Make sure there are no duplicates
            return cookie


def get_chat_history(message_queue: MessageQueue) -> Sequence[str]:
    return message_queue.get_messages_formatted()


def _get_nickname(cookie: str) -> str:
    if cookie not in ACCOUNTS.keys():
        raise AccountNotFoundException("No nickname claimed for cookie")
    return ACCOUNTS[cookie]


def _get_timestamp() -> float:
    time_now = datetime.datetime.now()
    return (time_now - EPOCH) / datetime.timedelta(seconds=1)


def _publish_message(message: Message, publish_socket: zmq.Socket):
    message_str = message.formatted()
    _logger.info("CHAT: {}".format(message_str))
    publish_socket.send_string("ALL {}".format(message_str))


def send_message(cookie: str,
                 message_str: str,
                 message_queue: MessageQueue,
                 publish_socket: zmq.Socket):
    # Publish & store
    msg_timestamp = _get_timestamp()
    nickname = _get_nickname(cookie)
    message = Message(msg_timestamp, nickname, message_str)
    message_queue.add_message(message)
    _publish_message(message, publish_socket)
