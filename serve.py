#!/usr/bin/env python3
import http.server
import socketserver
import os

os.chdir(r'C:\Users\wonde\studyweb\wonderwiki')
PORT = 19999

handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), handler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
