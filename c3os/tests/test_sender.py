import socket
import time
import threading
import json
import signal
import socketserver

socketserver.ThreadingTCPServer.allow_reuse_address = True
UUID_LEN = 32
monitor_ins_id = 'ab8bd7be5102545ea70d092b333d6631ab8bd7be5102545ea70d092b333d66314ec7c545c4504d3b89de49f067ce76c0'


class TCPHandler(socketserver.BaseRequestHandler):
    """
    TCP listen
    """

    def handle(self):
        # TODO: zmq
        data = self.request.recv(1024).strip().decode('utf-8')
        print(data)
        self.request.sendall(bytes(str(True), 'utf-8'))


class ThreadingTCPServer(socketserver.ThreadingTCPServer):
    pass


def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def send_instance_info():
    try:
        HOST, PORT = "localhost", 10006
        f = open('./test.json', 'r')
        data = str(json.load(f))
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect((HOST, PORT))
            sock.sendall(bytes(data, "utf-8"))

            # Receive data from the server and shut down
            received = str(sock.recv(1024), "utf-8")

        # print("Sent:     {}".format(data))
        # print("Received: {}".format(received))
    except:
        pass


def send_check_instance():
    try:
        HOST, PORT = "localhost", 10007
        data = monitor_ins_id
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect((HOST, PORT))
            sock.sendall(bytes(data, "utf-8"))

            # Receive data from the server and shut down
            received = str(sock.recv(1024), "utf-8")

        # print("Sent:     {}".format(data))
        # print("Received: {}".format(received))
    except:
        pass

# Create a socket (SOCK_STREAM means a TCP socket)
interrupted = False
signal.signal(signal.SIGINT, signal_handler)
DB_HOST, DB_PORT = 'localhost', 10009
db_server = ThreadingTCPServer((DB_HOST, DB_PORT), TCPHandler)
t = threading.Thread(target=db_server.serve_forever)
t.setDaemon(True)
t.start()
while True:
    t = threading.Thread(target=send_instance_info)
    t.setDaemon(True)
    t.start()

    t = threading.Thread(target=send_check_instance)
    t.setDaemon(True)
    t.start()

    if interrupted:
        break
