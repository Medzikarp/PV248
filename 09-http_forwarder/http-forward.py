from http.server import HTTPServer, BaseHTTPRequestHandler
import sys
import http.client
import ssl
import socket
import json
import OpenSSL.crypto as crypto
import os


class Server(HTTPServer):
    def serve_forever(self, upstream):
        self.RequestHandlerClass.upstream = upstream
        HTTPServer.serve_forever(self)


def get_hostname_path(url):
    url = url.replace("https://", "")
    url = url.replace("http://", "")
    hostname = url.split("/", 1)[0]
    parts = url.split("/", 1)
    path = None
    if len(parts) > 1:
        path = "/" + parts[1]
    return hostname, path


def execute_request(method, upstream, headers, content, timeout=1):
    if "https" in upstream:
        hostname, path = get_hostname_path(upstream)
        ctx = ssl.create_default_context()
        ctx.load_default_certs()
        print("Loading CA from " + ssl.get_default_verify_paths().openssl_cafile)
        conn = http.client.HTTPSConnection(hostname, context=ctx, timeout=timeout)
        conn.request(method, path, content, headers=headers)
        response = conn.getresponse()
    else:
        hostname, path = get_hostname_path(upstream)
        conn = http.client.HTTPConnection(hostname, timeout=timeout)
        conn.request(method, path, content, headers=headers)
        response = conn.getresponse()
    return response


def get_charset(headers):
    charset = headers.get_content_charset()
    if not charset:
        return "latin1"
    else:
        return charset


def get_certificate_san(x509cert):
    san = ''
    ext_count = x509cert.get_extension_count()
    for i in range(0, ext_count):
        ext = x509cert.get_extension(i)
        if 'subjectAltName' in str(ext.get_short_name()):
            san = ext.__str__()
    return san


def get_ssl_hosts(hostname):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((hostname, 443))
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    s = ctx.wrap_socket(s, server_hostname=hostname)

    # get certificate
    cert_bin = s.getpeercert(True)
    x509 = crypto.load_certificate(crypto.FILETYPE_ASN1,cert_bin)
    san = get_certificate_san(x509)
    hosts = []
    hosts.append(x509.get_subject().CN)
    items = [x.strip() for x in san.split(',')]
    for item in items:
        prefix = "DNS:"
        if item.startswith(prefix):
            item = item[len(prefix):]
        if item not in hosts:
            hosts.append(item)
    return hosts


def format_headers(headers):
    new_headers = {}
    for header in headers:
        new_headers[header[0]] = header[1]
    return new_headers

class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        json_response = {}
        response = None
        headers_to_send = self.headers
        if "Host" in headers_to_send and "localhost" in headers_to_send["Host"]:
            del headers_to_send["Host"]
        try:
            response = execute_request("GET", self.upstream, headers_to_send, None)
        except socket.timeout:
            json_response["code"] = "timeout"
        except ssl.SSLError as ex:
            print(ex)
            json_response["certificate valid"] = "false"

        json_data = None
        if response:
            if not json_response.get("code"):
                json_response["code"] = response.status
            json_response["headers"] = format_headers(response.getheaders())
            charset = get_charset(response.headers)
            body = response.read().decode(charset)
            try:
                json_data = json.loads(body)
                json_response["json"] = json_data
            except Exception as e:
                print("Unable to parse json body", e)
                json_response["content"] = body

        if "https://" in upstream:
            if not json_response.get("certificate valid"):
                json_response["certificate valid"] = "true"
            hostname, _ = get_hostname_path(upstream)
            hosts = get_ssl_hosts(hostname)
            if hosts is not None:
                json_response["certificate for"] = hosts

        self.send_response(200)
        self.send_header('Content-Type', 'application/json;charset=utf-8')
        self.end_headers()
        self.wfile.write(bytes(json.dumps(json_response, indent=2), "UTF-8"))

    def do_POST(self):
        json_response = {}
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode(get_charset(self.headers))
        response = None
        try:
            json_data = json.loads(post_data)
            method = json_data["type"]
            if method is not "GET" and not "POST":
                method = "GET"
            url = json_data["url"]
            content = json_data["content"]
            timeout = int(json_data["timeout"])
            headers = format_headers(json_data["headers"])
            response = execute_request(method, url, headers, content, timeout)
        except socket.timeout:
            json_response["code"] = "timeout"
        except ssl.SSLError as ex:
            print(ex)
            json_response["certificate valid"] = "false"
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
            try:
                if body:
                    json_data = json.loads(body)
                    json_response["json"] = json_data
                else:
                    json_response["json"] = ""
            except Exception as e:
                print("Unable to parse json body", e)
                json_response["content"] = body

        if "https://" in upstream:
            if not json_response.get("certificate valid"):
                json_response["certificate valid"] = "true"
            hostname, _ = get_hostname_path(url)
            hosts = get_ssl_hosts(hostname)
            if hosts is not None:
                json_response["certificate for"] = hosts

        self.send_response(200)
        self.send_header('Content-Type', 'application/json;charset=utf-8')
        self.end_headers()
        self.wfile.write(bytes(json.dumps(json_response, indent=2), "UTF-8"))


port = int(sys.argv[1])
upstream = sys.argv[2]
server = Server(('', port), RequestHandler)
server.serve_forever(upstream)
print('Listening on localhost:%s' % port)

