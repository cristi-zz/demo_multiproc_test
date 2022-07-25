import pytest
import logging
import logging.handlers
import sys
import multiprocessing as mp
import multiprocessing.managers

@pytest.fixture()
def memlogger(proxy_manager):
    """
    Adds a memory logger to the root logger and collects all the logging messages.

    The system must be in test mode, eg, no loggers with propagate==false present.
    Use misc.assert_no_errors_in_logs to observe if there are any errors in the log.
    """
    mem_handler = logging.handlers.MemoryHandler(capacity=100000, flushLevel=logging.CRITICAL + 1, flushOnClose=False)
    mem_handler.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    log_queue = proxy_manager.Queue(-1)
    q_handler = logging.handlers.QueueHandler(log_queue)
    listener = logging.handlers.QueueListener(log_queue, mem_handler, console_handler)

    root_log = logging.getLogger()
    root_log.addHandler(q_handler)
    root_log.setLevel(logging.DEBUG)

    listener.start()

    yield mem_handler

    listener.enqueue_sentinel()
    listener.stop()
    mem_handler.close()


@pytest.fixture(scope="session")
def proxy_manager():
    """
    Creates a syncmanager and returns it to be used in various contexts.

    :return:
    """
    manager = mp.managers.SyncManager()
    manager.start()

    yield manager

    manager.shutdown()
    manager.join(1)
