import os
import sys
import urllib2
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

BIND_ADDR = os.environ.get("BIND_ADDR", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "80"))
URL_PREFIX = os.environ.get("URL_PREFIX", "").rstrip('/') + '/'
SPARK_MASTER_HOST = ""


class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # redirect if we are hitting the home page
        if self.path in ("", URL_PREFIX):
            self.send_response(302)
            self.send_header("Location", URL_PREFIX + "proxy:" + SPARK_MASTER_HOST)
            self.end_headers()
            return
        self.proxyRequest(None)

    def do_POST(self):
        length = int(self.headers.getheader('content-length'))
        postData = self.rfile.read(length)
        self.proxyRequest(postData)

    def proxyRequest(self, data):
        targetHost, path = self.extractUrlDetails(self.path)
        targetUrl = "http://" + targetHost + path

        print("get: " + self.path)
        print("host: " + targetHost)
        print("path: " + path)
        print("target: " + targetUrl)

        proxiedRequest = urllib2.urlopen(targetUrl, data)
        resCode = proxiedRequest.getcode()

        if resCode == 200:
            page = proxiedRequest.read()
            page = self.rewriteLinks(page, targetHost)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(page)
        elif resCode == 302:
            self.send_response(302)
            self.send_header("Location", URL_PREFIX + "proxy:" + SPARK_MASTER_HOST)
            self.end_headers()
        else:
            raise Exception("Unsupported response: " + resCode)

    def extractUrlDetails(self, path):
        if path.startswith(URL_PREFIX + "proxy:"):
            start_idx = len(URL_PREFIX) + 6  # len('proxy:') == 6
            idx = path.find("/", start_idx)
            targetHost = path[start_idx:] if idx == -1 else path[start_idx:idx]
            path = "" if idx == -1 else path[idx:]
        else:
            targetHost = SPARK_MASTER_HOST
            path = path
        return (targetHost, path)

    def rewriteLinks(self, page, targetHost):
        target = "{0}proxy:{1}/".format(URL_PREFIX, targetHost)
        page = page.replace('href="/', 'href="' + target)
        page = page.replace('href="log', 'href="' + target + 'log')
        page = page.replace('href="http://', 'href="' + URL_PREFIX + 'proxy:')
        page = page.replace('src="/', 'src="' + target)
        page = page.replace('action="', 'action="' + target)
        return page


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: <proxied host:port> [<proxy port>]")
        sys.exit(1)

    SPARK_MASTER_HOST = sys.argv[1]

    if len(sys.argv) >= 3:
        SERVER_PORT = int(sys.argv[2])

    print("Starting server on http://{0}:{1}".format(BIND_ADDR, SERVER_PORT))

    server_class = HTTPServer
    server_address = (BIND_ADDR, SERVER_PORT)
    httpd = server_class(server_address, ProxyHandler)
    httpd.serve_forever()
