#  coding: utf-8 
import socketserver, os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        # Initialize status code 200
        self.ok_200 = 'HTTP/1.1 200 OK\r\n'
        # Header response 
        self.data = self.request.recv(1024).strip().decode('utf-8')
        # Get path from request
        path = self.path()

        # Webserver can only handle GET, not POST/PUT/DELETE
        if self.is_get():
            # Check if path is base directory
            if path[-1] == '/':
                path+='index.html'
            # Check if file path exists
            if self.valid_path('./www' + path):

                # Check what type of file the file path is
                if path.endswith('.html'):
                    self.handle_html(path)
                elif path.endswith('.css'):
                    self.handle_css(path)
                else:
                    # Status code 301 if no "/" at the end of path
                    self.handle_301_moved(path)
            else:
                # Return 404 Not found if file path does not exist
                self.handle_404_not_found()
        else:
            # Return 405 Method not allowed since can only handle GET
            self.handle_405()
            
    def handle_404_not_found(self):
        # Handle sending status code 404 if file path does not exist
        # Send basic html as well
        status_404 = ('HTTP/1.1 404 Not Found\r\n'
                      'Content-type: text/html\r\n\r\n')
        body = ('<!DOCTYPE html>'
                '<head><meta charset="UTF-8"></head>'
                '<html><body><center><h1>404 not found!</h1></center></body></html>\n')
        
        self.request.sendall(bytearray(status_404 + body,'utf-8'))

    def handle_405(self):
        # Handle sending status code 405 if methods other than GET is used
        status_405 = 'HTTP/1.1 405 Method Not Allowed\r\n\r\n'
        self.request.sendall(bytearray(status_405,'utf-8'))

    def handle_301_moved(self, path):
        # Handle status code 301
        # Move to correct file location
        status_301 = "HTTP/1.1 301 Moved Permanently\r\n"
        content_type = "Content-Type: text/plain\r\n"
        path += '/'
        self.request.sendall(bytearray(status_301 + content_type + "Location: {0}\r\n\r\n".format(path),"utf-8"))
    
    def handle_html(self, path):
        # Handle requests of type .html
        # Send status code 200
        self.request.sendall(bytearray(self.ok_200,'utf-8'))
        content = self.read_file(path)
        self.request.sendall(b'Content-Type: text/html\r\n\r\n')
        self.request.sendall(content)
    
    def handle_css(self, path):
        # Handle requests of type .css
        # Send status code 200
        self.request.sendall(bytearray(self.ok_200,'utf-8'))
        content = self.read_file(path)
        self.request.sendall(b'Content-Type: text/css\r\n\r\n')
        self.request.sendall(content)
        
    def is_get(self) -> bool:
        # Check if the header is GET, if so return True, otherwise False
        # First element of data is header
        return(self.data.split()[0] == 'GET')
    
    def path(self) -> str:
        # Gets the specified path
        # Second elemnt of data is file path
        return(self.data.split()[1])
    
    def valid_path(self, path) -> bool:
        # Check if file path exists
        # resource: https://www.freecodecamp.org/news/how-to-check-if-a-file-exists-in-python/
        return os.path.exists(path)
    
    def read_file(self, path) -> bytearray:
        # Read specified file and return as byte
        with open('./www' + path, 'r') as readfile:
            content = readfile.read()
            
        return bytearray(content,'utf-8')


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
