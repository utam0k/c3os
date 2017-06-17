from c3os import utils as U
from c3os.cntl import server


def start():
    """ Starting cntl. """
    U.start_thread(server.start)
