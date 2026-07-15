import http.server
import socketserver
import os

PORT = 8080
DIRECTORY = "frontend"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

if __name__ == "__main__":
    os.makedirs(DIRECTORY, exist_ok=True)
    if not os.path.exists(os.path.join(DIRECTORY, "index.html")):
        print(f"Error: index.html not found in {DIRECTORY}")
    else:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Server started at http://localhost:{PORT}")
            print(f"Serving files from: {os.path.abspath(DIRECTORY)}")
            httpd.serve_forever()
