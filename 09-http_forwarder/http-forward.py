from http.server import HTTPServer, BaseHTTPRequestHandler
import sys
import http.client
import ssl
import socket
import json


class Server(HTTPServer):
    def serve_forever(self, upstream):
        self.RequestHandlerClass.upstream = upstream
        HTTPServer.serve_forever(self)


def execute_request(method, upstream, headers, content, timeout=1):
    if "https" in upstream:
        url = upstream.replace("https://", "")
        domain = url.split("/", 1)[0]
        path = "/" + url.split("/", 1)[1]
        conn = http.client.HTTPSConnection(domain, context=ssl._create_unverified_context(), timeout=1)
        conn.request(method, path, content, headers=headers)
        response = conn.getresponse()
    else:
        url = upstream.replace("http://", "")
        domain = url.split("/", 1)[0]
        path = "/" + url.split("/", 1)[1]
        conn = http.client.HTTPConnection(domain, timeout=1)
        conn.request(method, path, content, headers=headers)
        response = conn.getresponse()
    return response


def get_charset(headers):
    charset = headers.get_content_charset()
    if not charset:
        return "latin1"
    else:
        return charset


class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        json_response = {}
        response = None;
        try:
            response = execute_request("GET", self.upstream, self.headers, None)
        except socket.timeout:
            json_response["code"] = "timeout"

        json_data = None
        if response:
            if not json_response.get("code"):
                json_response["code"] = response.status
            json_response["headers"] = response.getheaders()
            charset = get_charset(response.headers)
            body = response.read().decode(charset)
            try:
                json_data = json.loads(body)
                json_response["json"] = json_data
            except Exception as e:
                print("Unable to parse json body", e)
                json_response["content"] = body

        self.send_response(200)
        self.send_header('Content-Type', 'application/json;charset=utf-8')
        self.end_headers()
        self.wfile.write(bytes(json.dumps(json_response), "UTF-8"))

    def do_POST(self):
        json_response = {}
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode(get_charset(self.headers))
        response = None
        try:
            json_data = json.loads(post_data)
            method = json_data["type"]
            if method is not "GET" or not "POST":
                method = "GET"
            url = json_data["url"]
            content = json_data["content"]
            timeout = json_data["timeout"]
            headers = json_data["headers"]
            response = execute_request(method, url, headers, content, timeout)
        except Exception as ex:
            print(ex)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(json.dumps({"json": "invalid json"}), "UTF-8"))
            return

        if response:
            json_response["headers"] = response.getheaders()
            charset = get_charset(response.headers)
            body = response.read().decode(charset)
            body = body if body else ""
            try:
                if body:
                    json_data = json.loads(body)
                    json_response["json"] = json_data
                else:
                    json_response["json"] = ""
            except Exception as e:
                print("Unable to parse json body", e)
                json_response["content"] = body

            self.send_response(200)
            self.send_header('Content-Type', 'application/json;charset=utf-8')
            self.end_headers()
            self.wfile.write(bytes(json.dumps(json_response), "UTF-8"))




port = int(sys.argv[1])
upstream = sys.argv[2]
server = Server(('', port), RequestHandler)
server.serve_forever(upstream)
print('Listening on localhost:%s' % port)

