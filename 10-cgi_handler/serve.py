from http.server import HTTPServer, CGIHTTPRequestHandler
from socketserver import ThreadingMixIn
import sys
import os


class ThreadingServer(ThreadingMixIn, HTTPServer):
    pass


class RequestHandler(CGIHTTPRequestHandler):

    def do_GET(self):
        url_path = self.path.split("?")[0]
        if url_path.endswith(".cgi") or ".cgi/" in url_path:
            self.cgi_info = "", self.path[1:]
            self.run_cgi()
        else:
            self.serve_text()

    def do_POST(self):
        url_path = self.path.split("?")[0]
        if url_path.endswith(".cgi") or ".cgi/" in url_path:
            self.cgi_info = "", self.path[1:]
            self.run_cgi()
        else:
            self.serve_text()

    def serve_text(self):
        local_path = self.path.split("?")[0]
        abs_path = os.getcwd() + local_path
        if os.path.isfile(abs_path):
            file_size = os.path.getsize(abs_path)
            self.send_response(200)
            self.send_header('Content-Length', str(file_size))
            with open(abs_path, "rb") as f:
                while True:
                    c = f.read(1024)
                    if not c:
                        break
                    self.wfile.write(c)
        else:
            print("serve_text: " + abs_path)
            self.send_error(404)


port = int(sys.argv[1])
if len(sys.argv) == 3:
    content_dir = sys.argv[2]
    os.chdir(content_dir)

server = ThreadingServer(('', port), RequestHandler)
server.serve_forever()
print('Listening on localhost:%s' % port)

