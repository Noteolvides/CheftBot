import logging


def startLogger():
    logging.basicConfig(filename="logger.log",
                        format='%(asctime)s %(message)s',
                        filemode='w')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    return logger
