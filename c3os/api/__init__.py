import multiprocessing as mp

from c3os.api.server import APIServer, APIHandler
from c3os import conf

CONF = conf.CONF


def start():
    """ Starting api server. """
    HOST, PORT = CONF['server']['address'], int(CONF['server']['port'])
    api_server = APIServer((HOST, PORT), APIHandler)
    mp.Process(target=api_server.serve_forever).start()
