"""The server handler implemented using Python Flask. This module forms the core
of the service by mapping the requests from clients into functions provided by
server_func.
"""
import logging

from flask import Flask
from flask import make_response
from flask import request
from flask import Response

import server_func as functions

app = Flask(__name__)
_logger = logging.getLogger("SERVER")
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s:%(levelname)s: %(message)s")


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
    resp.set_cookie('cookie', cookie)
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


@app.route("/send-message")
def send_message(nickname: str, channel: str, message: str):
    # Validate nickname
    # TODO: Consider whether to include timestamp in the message
    # Add "timestamp - nickname - message" to the channel
    # Publish message
    return


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
    app.run()
