# -*- coding: utf-8 -*-
from threading import Thread

class MessageReceiver(Thread):
    def __init__(self, client):
        self.client = client
        super(MessageReceiver, self).__init__()

    def run(self):
        while True:
            data = self.client.connection.recv(1024).strip()
            if data:
               self.client.receive_message(data)
