# -*- coding: utf-8 -*-
from threading import Thread

class MessageReceiver(Thread):
    def __init__(self, client):
        self.client = client
        super(MessageReceiver, self).__init__()
        self.daemon = True

    def run(self):
        while True:
            data = self.client.connection.recv(1048576).strip()
            if data:
               self.client.receive_message(data)
