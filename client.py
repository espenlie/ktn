# -*- coding: utf-8 -*-
import socket, json, sys
from messagereceiver import MessageReceiver

class Client:
    def __init__(self, host, server_port):
        self.host = host
        self.server_port = server_port
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.run()

    def run(self):
        self.connection.connect((self.host, self.server_port))
        recv_thread = MessageReceiver(self)
        recv_thread.start()
        print "Client recieve thread %s" % recv_thread.name

    def disconnect(self):
        self.connection.close()

    def receive_message(self, message):
        payload = json.loads(message)
        print "%s: %s <%s> %s" % (payload.get('timestamp'), payload.get('response'), payload.get('sender'), payload.get('content'))

    def send_payload(self, data):
        s = data.split(' ', 1)
        payload = {'request': s[0], 'content': s[1] if len(s) > 1 else None}
        self.connection.sendall(json.dumps(payload))

if __name__ == '__main__':
    client = Client(sys.argv[1], 9000)
    while True:
        message = raw_input('')
        client.send_payload(message)
        if message == 'logout':
            break
    client.disconnect()
