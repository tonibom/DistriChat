"""The server handler implemented using Python Flask. This module forms the core
of the service by mapping the requests from clients into functions provided by
server_func.
"""
import json
import logging

from flask import Flask
from flask import make_response
from flask import request
from flask import Response

import server_func as functions

MESSAGE_QUEUE = functions.MessageQueue()
publish_port = None
publish_socket = None

app = Flask(__name__)
_logger = logging.getLogger("SERVER")


@app.route("/claim-nick", methods=["POST"])
def claim_nick() -> Response:
    # Verify whether the nickname is available
    error_resp = make_response("Erroneous request\n")

    if request.method != "POST":
        _logger.debug("Request not POST!")
        return error_resp

    # nickname = request.args.get("nickname", "")
    nickname = request.form["nickname"]
    cookie = request.cookies.get("cookie")

    if nickname is "":
        _logger.debug("Request missing nickname!")
        return error_resp

    if cookie is None:
        cookie = functions.generate_cookie()

    _logger.info("Received nickname claim request for \"{}\" by {}.".format(nickname,
                                                                            cookie))

    response = functions.claim_nickname(nickname, cookie) + "\n"
    resp = make_response(response)
    resp.set_cookie("cookie", cookie)
    return resp


@app.route("/chat-history")
def chat_history() -> Response:
    error_resp = make_response("Erroneous request\n")

    if request.method != "GET":
        _logger.debug("Request not GET!")
        return error_resp

    _logger.info("Received chat history get request.")

    try:
        chatlog = functions.get_chat_history(MESSAGE_QUEUE)
        _logger.debug(chatlog)
        resp = make_response(json.dumps(chatlog))
        # resp = make_response("Chat history read successfully.\n")
    except Exception as e:
        _logger.warning("Unhandled exception at chat history get : %s", e)
        return error_resp
    return resp


@app.route("/client-address")
def client_address_for(nickname: str) -> str:
    # Client requests IP address of another client based on the nickname
    # Returns IP of client with the requested nickname
    # Meant for establishing P2P between clients
    return ""


@app.route("/ping")
def ping():
    return "pong\n"


@app.route("/send-message", methods=["POST"])
def send_message() -> Response:
    # Validate nickname
    # Add "timestamp - nickname - message" to the channel
    # Publish message
    error_resp = make_response("Erroneous request\n")

    if request.method != "POST":
        _logger.debug("Request not POST!")
        return error_resp

    message = request.form["message"]
    cookie = request.cookies.get("cookie")

    if cookie is None:
        _logger.debug("Request missing cookie!")
        return error_resp

    _logger.info("Received request to send a message.")

    try:
        functions.send_message(cookie, message, MESSAGE_QUEUE, publish_socket)
        resp = make_response("Message sent successfully.\n")
    except functions.AccountNotFoundException:
        return make_response("You need to claim a nickname to be allowed to send messages!\n")
    except Exception as e:
        _logger.warning("Unhandled exception at message sending: %s", e)
        return error_resp

    resp.set_cookie("cookie", cookie)
    return resp


@app.route("/join")
def subscribe_channel(channel: str):
    # Client joins the channel specified (if it exists)
    # Address for connecting to PUB/SUB socket is returned
    return


@app.route("/synchronize")
def synchronize(timestamp: int):
    # Handle synchronization of clocks
    # Could omit this
    return


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s:%(levelname)s: %(message)s")
    publish_socket, port = functions.create_publish_socket()
    app.run()
