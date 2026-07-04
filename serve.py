#!/usr/bin/env python3
"""
WonderWiki - 记忆维基 前端静态服务器
用法: python serve.py
端口: 19999
"""
import http.server
import socketserver
import os

PORT = 19999

handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), handler) as httpd:
    print(f"WonderWiki frontend running at http://127.0.0.1:{PORT}")
    httpd.serve_forever()
