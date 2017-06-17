import socketserver

vm_ids = list(range(11))


class TCPHandler(socketserver.BaseRequestHandler):
    """
    TCP listen
    """

    def handle(self):
        global vm_ids
        data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        print(data)
        if int(data) in vm_ids:
            self.request.sendall(bytes(str(1), 'utf-8'))
        else:
            self.request.sendall(bytes(str(0), 'utf-8'))


def start_listen():
    HOST, PORT = "localhost", 10006

    server = socketserver.ThreadingTCPServer((HOST, PORT), TCPHandler)
    server.serve_forever()

if __name__ == "__main__":
    start_listen()
