import logging
import logging.config
import time


_logger = logging.getLogger("SERVER")


def main():

    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s:%(levelname)s: %(message)s")

    counter = 0
    while True:
        _logger.debug("Alive counter: %d", counter)
        time.sleep(1)
        counter = (counter + 1) % 101


if __name__ == "__main__":
    main()
