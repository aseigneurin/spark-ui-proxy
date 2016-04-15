import BaseHTTPServer
import urllib2

HOST_NAME = 'localhost'
PORT_NUMBER = 8888


class ProxyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(s):
        if s.path == "" or s.path == "/":
            s.send_response(302)
            s.send_header("Location", "/proxy:localhost:8080")
            s.end_headers()
            return

        if s.path.startswith("/proxy:"):
            idx = s.path.find("/", 7)
            path = "" if idx == -1 else s.path[idx:]
            targetHost = s.path[7:] if idx == -1 else s.path[7:idx]
        else:
            targetHost = "localhost:8080"
            path = s.path

        targetUrl = "http://" + targetHost + path

        print "get: " + s.path
        print "path: " + path
        print "host: " + targetHost
        print "target: " + targetUrl

        page = urllib2.urlopen(targetUrl).read()
        page = page.replace("href=\"/", "href=\"/proxy:{0}/".format(targetHost))
        page = page.replace("href=\"log", "href=\"/proxy:{0}/log".format(targetHost))
        page = page.replace("href=\"http://", "href=\"/proxy:")
        page = page.replace("src=\"/", "src=\"/proxy:{0}/".format(targetHost))

        s.send_response(200)
        s.end_headers()
        s.wfile.write(page)


if __name__ == '__main__':
    print "Starting server on http://{0}:{1}".format(HOST_NAME, PORT_NUMBER)

    server_class = BaseHTTPServer.HTTPServer
    server_address = (HOST_NAME, PORT_NUMBER)
    httpd = server_class(server_address, ProxyHandler)
    httpd.serve_forever()
