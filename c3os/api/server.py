import socketserver
import ast
import json

from c3os.objects.instance import Instance
from c3os.objects.region import Region
from c3os import db
from c3os import utils
from c3os import conf
from c3os.api import type0
from c3os.api.type import APITYPE
from c3os import messaging
from c3os.cntl.type import CNTLTYPE

socketserver.ThreadingTCPServer.allow_reuse_address = True
UUID_LEN = conf.UUID_LEN


class APIHandler(socketserver.BaseRequestHandler):
    """API Server handler

    Wrapper class from socketserver.BaseRequestHandeler.
    """

    def handle(self):
        """ Handling received message. """
        self.db_pool = self.server.db_pool
        # TODO: zmq
        data = ''
        while True:
            receive = self.request.recv(1024).strip().decode('utf-8')
            try:
                data += receive
                data = json.loads(data)
                break
            except:
                pass

        if int(data['type']) == APITYPE.ADD_DB:
            ret_message = type0.execute(self.db_pool, data["body"])
        elif int(data['type']) == APITYPE.CREATE_INSTANCE:
            data = json.dumps(
                {'type': CNTLTYPE.CREATE_INSTANCE, 'body': data['body']})
            messaging.publish(body=data)
        elif int(data['type']) == APITYPE.DELETE_INSTANCE:
            data = json.dumps(
                {'type': CNTLTYPE.DELETE_INSTANCE, 'body': data['body']})
            messaging.publish(body=data)
        else:
            ret_message = data['type'] + "is nothing api type"

        self.request.sendall(bytes(ret_message, 'utf-8'))


class APIServer(socketserver.ThreadingTCPServer):
    """API Server handler

    Wrapper class from socketserver.ThreadingTCPServer.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_pool = db.generate_pool()
        self.regions = {}
