#!/usr/bin/env python3
"""
Simple local web server for K3 Vocabulary Practice.
Run: python server.py
Then open: http://localhost:8000/K3.html
"""

import http.server
import socketserver
import webbrowser
import os

PORT = 8080
DIR  = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def log_message(self, format, *args):
        # Suppress 304 Not Modified noise, keep others
        if args[1] != "304":
            super().log_message(format, *args)

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    url = f"http://localhost:{PORT}/K3-Sound.html"
    print(f"Serving K3 Vocabulary Practice at {url}")
    print("Press Ctrl+C to stop.\n")
    webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
