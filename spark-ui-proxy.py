import BaseHTTPServer
import sys
import urllib2

HOST_NAME = 'localhost'
PORT_NUMBER = 0
ROOT = ""


class ProxyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        self.proxyRequest(None)

    def do_POST(self):
        length = int(self.headers.getheader('content-length'))
        postData = self.rfile.read(length)
        self.proxyRequest(postData)

    def proxyRequest(self, data):
        if self.path == "" or self.path == "/":
            self.send_response(302)
            self.send_header("Location", "/proxy:" + ROOT)
            self.end_headers()
            return

        if self.path.startswith("/proxy:"):
            idx = self.path.find("/", 7)
            path = "" if idx == -1 else self.path[idx:]
            targetHost = self.path[7:] if idx == -1 else self.path[7:idx]
        else:
            targetHost = ROOT
            path = self.path

        targetUrl = "http://" + targetHost + path

        print "get: " + self.path
        print "path: " + path
        print "host: " + targetHost
        print "target: " + targetUrl

        page = urllib2.urlopen(targetUrl, data).read()
        page = page.replace("href=\"/", "href=\"/proxy:{0}/".format(targetHost))
        page = page.replace("href=\"log", "href=\"/proxy:{0}/log".format(targetHost))
        page = page.replace("href=\"http://", "href=\"/proxy:")
        page = page.replace("src=\"/", "src=\"/proxy:{0}/".format(targetHost))

        self.send_response(200)
        self.end_headers()
        self.wfile.write(page)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "Usage: <proxied host:port> <proxy port>"
        sys.exit(1)

    ROOT = sys.argv[1]
    PORT_NUMBER = int(sys.argv[2])

    print "Starting server on http://{0}:{1}".format(HOST_NAME, PORT_NUMBER)

    server_class = BaseHTTPServer.HTTPServer
    server_address = (HOST_NAME, PORT_NUMBER)
    httpd = server_class(server_address, ProxyHandler)
    httpd.serve_forever()
