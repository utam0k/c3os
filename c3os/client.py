import socket
import json
import time
import multiprocessing as mp

from c3os import utils
from c3os import conf
from c3os import db
from c3os.api.type import APITYPE

CONF = conf.CONF


def start():
    """ Start client service """

    mp.Process(target=client).start()


def client():
    """ client main routine """

    db_pool = db.generate_pool()
    while True:
        send_db(db_pool)
        time.sleep(3.0)


def send_db(db_pool):
    """Information on its DB is sent to other c3os.

    Args:
        db_pool (DBPool): DBPool class.
    Returns:
        None:
    """

    all_instance_info = utils.to_dict(db_pool)
    all_region_names = [name for name in all_instance_info.keys()]
    for dest_region_name, dest in CONF['dests'].items():
        host, port = dest.split(',')
        for region_name in all_region_names:
            if dest_region_name.lower() == region_name.lower():
                all_instance_info.pop(region_name)
                break

        db_info = json.dumps(all_instance_info)
        data = json.dumps({'type': APITYPE.ADD_DB, 'body': db_info})
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((host, int(port)))
                sock.sendall(bytes(data, "utf-8"))
        except:
            print("Error: Connected", host, port)
