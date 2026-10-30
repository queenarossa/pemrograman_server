# server.py
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
class SimpleHandler(BaseHTTPRequestHandler):
    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)
    def do_GET(self):
        if self.path == "/":
            self.send_json({"message": "Simple LMS Backend"})
        elif self.path == "/health":
            self.send_json({"status": "ok"})
        elif self.path == "/courses":
            self.send_json({"courses": [
                {"id": 1, "name": "Pemrograman Sisi Server"},
                {"id": 2, "name": "Basis Data"}
            ]})
        elif self.path == "/students":
            self.send_json({"students": [
                {"id": 1, "name": "Andi"},
                {"id": 2, "name": "Siti"}
            ]})
        elif self.path == "/assignments":
            self.send_json({"assignments": [
                {"id": 1, "title": "Backend Fundamentals"}
            ]})
        else:
            self.send_json({"detail": "Not Found"}, 404)
server = HTTPServer(("localhost", 8000), SimpleHandler)
print("Server running at http://localhost:8000")
server.serve_forever()