# -*- coding: utf-8 -*-
import SocketServer, re, time, json


class ClientHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        self.ip = self.client_address[0]
        self.port = self.client_address[1]
        self.connection = self.request
    
        print "New client connected @ %s %s" % (self.ip, self.port)
        # Loop that listens for messages from the client
        while True:
            received_string = self.connection.recv(4096).strip()
            if received_string:
                payload = json.loads(received_string)
                request = payload.get('request')
                if request == 'login':
                    self.login(payload)
                elif request == 'logout':
                    self.logout(payload)
                elif request == 'msg':
                    self.msg(payload)
                elif request == 'names':
                    self.names(payload)
                elif request == 'help':
                    self.help(payload)
                else:
                    self.error(payload)
            else:
                break

    def login(self, payload):
        username = re.sub('[^0-9a-zA-Z]+', '*', payload.get('content'))
        while username in self.server.clients.values():
            username += '*'
        self.server.clients[self.connection] = username
        self.send_payload('server', 'info', 'Successfully logged in as %s' % username)
        msg_string = '\n'
        if self.server.messages:
            for payload in self.server.messages:
                msg_string += "%s: <%s> %s %s\n" % (payload.get('timestamp'), payload.get('sender'), payload.get('response'), payload.get('content'))
            self.send_payload('server', 'info', msg_string)
    def logged_in(self):
        if not self.connection in self.server.clients:
            self.send_payload('server', 'error', 'Not logged in. Type help for info.')
            return False
        else:
            return True

    def logout(self, payload):
        if self.logged_in():
            username = self.server.clients[self.connection]
            self.send_payload('server', 'info', 'Successfully logged out')
            del self.server.clients[self.connection]

    def msg(self, payload):
        if self.logged_in():
            username = self.server.clients[self.connection]
            msg = payload.get('content')
            self.send_payload(username, 'message', msg)

    def names(self, payload):
        if self.logged_in():
            names = self.server.clients.values()
            self.send_payload('server', 'info', ', '.join(names))

    def help(self, payload):
        help_string = '\nlogin <username> - log in with the given username\nlogout - log out\nmsg <message> - send message\nnames - list users in chat\nhelp - view help text'
        self.send_payload('server', 'info', help_string)
        

    def send_payload(self, sender, response, content):
        payload = {'timestamp'  : time.strftime('%Y-%m-%d %H:%M:%S'),
                    'sender'    : sender,
                    'response'  : response,
                    'content'   : content
        }
        if response == 'message':
            self.server.messages.append(payload)
            self.server.broadcast(json.dumps(payload))
        else:
            self.connection.sendall(json.dumps(payload))
    
    def error(self, payload):
        self.send_payload('server', 'error', 'You did somethin wrong: %s' % payload.get('request'))


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):

    """
    This class is present so that each client connected will be ran as a own
    thread. In that way, all clients will be served by the server.

    No alterations is necessary
    """
    allow_reuse_address = True
    messages = []
    clients = {}

    def broadcast(self, message):
        for client in self.clients:
            client.sendall(message)

if __name__ == "__main__":
    """
    This is the main method and is executed when you type "python Server.py"
    in your terminal.

    No alterations is necessary
    """
    HOST, PORT = '193.35.52.79', 9000
    print 'Server running...'

    # Set up and initiate the TCP server
    server = ThreadedTCPServer((HOST, PORT), ClientHandler)
    server.serve_forever()
