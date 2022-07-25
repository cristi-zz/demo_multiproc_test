import logging

"""
The code here prints some text, guarded by a maximum size. If that size is exceeded, an exception will be raised.

"""

def max_msg_length():
    """
    It will be used for mocking demonstrations
    """
    return 10

def display_function(message):
    """
    If one mocks print directly, it will interfere with other prints from the python (eg. exceptions)
    """
    print(message)


def side_effect_function(message):
    """
    Prints a message under a certain length. Raise an exception if the message is too long.

    :param message:
    :return:
    """
    msg_len_exception = max_msg_length()
    if len(message) > msg_len_exception:
        raise Exception("Message too long")
    display_function(message)
    return len(message)


def worker_function(no_messages, message_stem):
    """
    This function will print increasingly long messages. In case of exception, a log entry will be added and the
    exception is propagated.

    :param no_messages:
    :param message_stem:
    :return:
    """
    L = logging.getLogger()
    L.setLevel(logging.DEBUG)
    L.info("Starting the messaging output")
    for m in range(no_messages):
        message = message_stem + " ".join([f"{m}"] * m)
        try:
            side_effect_function(message)
        except:
            L.exception("Side effect function had an error")
            raise
