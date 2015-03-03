# -*- coding: utf-8 -*-
import SocketServer, re, time, json, sys

class ClientHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        self.ip = self.client_address[0]
        self.port = self.client_address[1]
        self.connection = self.request
    
        print "New client connected @ %s %s" % (self.ip, self.port)
        while True:
            received_string = self.connection.recv(4096).strip()
            print received_string
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
            username += '_'
        nick_colors = ['\033[0;30m','\033[1;31m', '\033[0;32m','\033[0;33m','\033[0;34m','\033[0;35m','\033[0;36m','\033[0;37m'] 
        username = nick_colors[randint(0, 7)] + username
        self.server.clients[self.connection] =  username
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
            self.send_payload(username+'\003[0m', 'message', msg)

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
    allow_reuse_address = True
    messages = []
    clients = {}
    def broadcast(self, message):
        for client in self.clients:
            client.sendall(message)

if __name__ == "__main__":
    HOST, PORT = sys.argv[1], 9000
    print 'Server running...'
    server = ThreadedTCPServer((HOST, PORT), ClientHandler)
    server.serve_forever()
