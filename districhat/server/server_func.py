"""The server functions collection as a separate module so that the handler for
the web requests can be implemented separately. This modular separation allows
for changing to using different frameworks for the actual server request handler
implementation whilst keeping the server functionality intact.
"""
import logging
import random
import string

# TODO: Placeholder
ACCOUNTS = {"cookie1": "Janne",
            "cookie2": "Metsuri",
            "cookie3": "Pirkka-Pekka",
            }
COOKIE_LENGTH = 10

_logger = logging.getLogger("SERVER-FUNCTIONS")


def add_message(chatroom, nickname, message):
    # Publish & store
    return


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


def generate_cookie() -> str:
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(COOKIE_LENGTH)])


def get_chat_history():
    return


def subscribe(chatroom: str):
    # Not entirely sure how this'll evolve, but this is here as a reminder
    return


def synchronize():
    # Could omit this
    return
