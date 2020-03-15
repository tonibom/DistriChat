"""CLI User interface for the client"""
import enum
import logging

from typing import Optional, Sequence, Tuple


class MenuOptions(enum.Enum):
    HELP = 0
    SERVER = 1
    CHAT_HISTORY = 2
    CLAIM_NICKNAME = 3
    JOIN_SERVER = 4
    SEND_MESSAGE = 5
    QUIT = 6


MENU_COMMANDS = {
    "HELP": MenuOptions.HELP,
    "H": MenuOptions.HELP,
    "?": MenuOptions.HELP,

    "SERVER": MenuOptions.SERVER,

    "CHAT-HISTORY": MenuOptions.CHAT_HISTORY,
    "CHATLOG": MenuOptions.CHAT_HISTORY,
    "PRINT-CHAT": MenuOptions.CHAT_HISTORY,

    "CLAIM-NICKNAME": MenuOptions.CLAIM_NICKNAME,
    "NICKNAME": MenuOptions.CLAIM_NICKNAME,
    "NICK": MenuOptions.CLAIM_NICKNAME,

    "JOIN": MenuOptions.JOIN_SERVER,
    "SUBSCRIBE": MenuOptions.JOIN_SERVER,
    "CONNECT": MenuOptions.JOIN_SERVER,

    "MESSAGE": MenuOptions.SEND_MESSAGE,
    "MSG": MenuOptions.SEND_MESSAGE,

    "QUIT": MenuOptions.QUIT,
    "Q": MenuOptions.QUIT,
    "EXIT": MenuOptions.QUIT,
    "SHUTDOWN": MenuOptions.QUIT,
    "CLOSE": MenuOptions.QUIT,
}

_MENU_COMMAND_INFO = {
    MenuOptions.HELP: {
        "name": ("HELP", "aliases: H, ?"),
        "description": "display information about available commands",
        "usage": "help <COMMAND>",
        "example": "help nickname",
        "parameter-count": (0, 1),
    },
    MenuOptions.SERVER: {
        "name": ("SERVER", "aliases: "),
        "description": "set the server address",
        "usage": "server <IP ADDRESS>",
        "example": "server 35.228.135.146",
        "parameter-count": (1, ),
    },
    MenuOptions.CHAT_HISTORY: {
        "name": ("CHAT-HISTORY", "aliases: CHATLOG, PRINT-CHAT"),
        "description": "print the chat history",
        "usage": "CHAT-HISTORY",
        "example": "CHAT-HISTORY",
        "parameter-count": (0, ),
    },
    MenuOptions.CLAIM_NICKNAME: {
        "name": ("CLAIM-NICKNAME", "aliases: NICKNAME, NICK"),
        "description": "select a nickname to use when chatting",
        "usage": "NICKNAME <NICKNAME>",
        "example": "NICKNAME user1234",
        "parameter-count": (1, ),
    },
    MenuOptions.JOIN_SERVER: {
        "name": ("JOIN", "aliases: SUBSCRIBE, CONNECT"),
        "description": "join the chatroom",
        "usage": "JOIN",
        "example": "JOIN",
        "parameter-count": (0, ),
    },
    MenuOptions.SEND_MESSAGE: {
        "name": ("MESSAGE", "aliases: MSG"),
        "description": "send a message to the chat",
        "usage": "MESSAGE <MESSAGE>",
        "example": "MSG This message shall be sent.",
        "parameter-count": (1, ),
    },
    MenuOptions.QUIT: {
        "name": ("QUIT", "aliases: Q, EXIT, SHUTDOWN, CLOSE"),
        "description": "close the application",
        "usage": "QUIT",
        "example": "QUIT",
        "parameter-count": (0, ),
    },
}

_logger = logging.getLogger("INTERFACE")
_PADDING = 32


def exit_application(nickname: str = None):
    if nickname is not None:
        print("Goodbye {}.".format(nickname))
    print("\nExiting application...")


def invalid_ip_address(ip_address: str):
    print("\nInvalid IP address: {}.".format(ip_address))


def invalid_parameter(parameter: str):
    print("\nInvalid parameter for command: '{}'.".format(parameter))


def invalid_parameter_count(command: MenuOptions, parameters: Sequence[str]):
    try:
        # TODO: Remove this check when all commands have been implemented
        expected_count = _MENU_COMMAND_INFO[command]["parameter-count"]
    except TypeError:
        _logger.warning("Tried to access unimplemented command's parameter count")
        return
    expected_count = [str(a) for a in expected_count]
    if len(expected_count) != 1:
        # There are multiple valid parameter counts
        expected_count = " or ".join(expected_count)
    else:
        expected_count = expected_count[0]
    print("Invalid number of parameters! ({})".format(len(parameters)))
    print("The command {} takes {} parameters.\n".format(command.name,
                                                         expected_count))
    print_command_usage(command)


def invalid_server_address(server_ip: str):
    print("Couldn't connect to {}. Check the address.".format(server_ip))


def main_menu() -> Optional[Tuple[MenuOptions, Sequence[str]]]:
    """User interface for the main menu structure. Provides the user the options
    to choose from and asks what the user wants to do. User inputs their choice,
    this selection is validated and responded to.
        Valid -> response to user + return appropriate command to be handled in core
        Invalid -> response to user + prompt to try again
    """

    print("\n{} MAIN MENU {}\n".format(_PADDING * "=", _PADDING * "="))

    while True:
        user_input = input("Enter command >").split(" ")
        input_command = user_input[0]
        input_parameters = user_input[1:]
        print("")
        if input_command.upper() in MENU_COMMANDS.keys():
            return MENU_COMMANDS[input_command.upper()], input_parameters
        else:
            print("Invalid command. Use command 'HELP' for help on commands.")


def missing_nickname():
    print("\nNo nickname set! You need to claim nickname before sending messages. "
          + "Use NICKNAME command to claim nickname.\n")


def missing_server_address():
    print("\nNo server address set! Set the server address using the SERVER command.")


def nickname_already_taken(reply_msg: str):
    print(reply_msg)


def nickname_claimed(reply_msg: str):
    print(reply_msg)


def message_sent(reply_msg: str):
    print(reply_msg)


def _print_available_commands():
    print("\nAvailable commands:")
    for i in _MENU_COMMAND_INFO.values():
        if type(i) is not int:
            # TODO: fix when all commands have been added
            print(i["name"])


def print_chat_log(messages: Sequence[str]):
    if len(messages) == 0:
        print("\nNo messages in chatlog.\n")
        return

    print("\n{} CHAT LOG {}\n".format(_PADDING * "-", _PADDING * "-"))
    i = 0
    for message in messages:
        i += 1
        print(message)
        if i % 5 == 0:
            # Print in sets of 5
            input("\n{} PRESS ENTER TO CONTINUE PRINTING {}".format(_PADDING * "-",
                                                                    _PADDING * "-"))
    print("{}".format((2 * _PADDING) * "-"))


def print_command_usage(command: MenuOptions):
    print("Usage: " + _MENU_COMMAND_INFO[command]["usage"])
    print("For help, run 'HELP {}'".format(_MENU_COMMAND_INFO[command]["name"][0]))


def print_help(command_in: MenuOptions = None):

    def print_command_info(cmd: MenuOptions):
        name = _MENU_COMMAND_INFO[cmd]["name"][0] \
               + " | " \
               + _MENU_COMMAND_INFO[cmd]["name"][1]
        print("Name: " + name)
        print("Description: " + _MENU_COMMAND_INFO[cmd]["description"])
        print("Usage: " + _MENU_COMMAND_INFO[cmd]["usage"])
        print("Example: " + _MENU_COMMAND_INFO[cmd]["example"])

    if command_in is not None:
        # TODO: Change when all commands implemented
        if type(_MENU_COMMAND_INFO[command_in]) == dict:
            print_command_info(command_in)
            return
        else:
            print("{} is a valid command, but not yet implemented".format(command_in))

    print("{} HELP {}\n".format(_PADDING * "=", _PADDING * "="))
    print("The commands are not case sensitive and have multiple aliases.")
    print("Some commands require parameters to be passed as well.")
    print("\n++++++++++ COMMANDS ++++++++++\n")
    for command in _MENU_COMMAND_INFO:
        # TODO: Change when all commands implemented
        if type(_MENU_COMMAND_INFO[command]) == dict:
            print_command_info(command)
        else:
            print("{} is a valid command, but not yet implemented".format(command))
        print("\n")


def unexpected_response(reply: str):
    print("The server responded unexpectedly: {}".format(reply))


def welcome():
    print("Welcome to DistriChat!\n")
