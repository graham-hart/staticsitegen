#!./env/bin/python

import argparse
import renderer
import http.server
import socketserver
import os

class DebugHTTPEventHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith("/"):
            self.path += "index.html"
        if not self.path.endswith(".html"):
            self.path = os.path.join("/site", self.path[1:])
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        self.path = os.path.join(renderer.SITE_DIR, 'content', self.path[1:-5] + ".md")


        # Sending an '200 OK' response
        self.send_response(200)

        # Setting the header
        self.send_header("Content-type", "text/html")

        # Whenever using 'send_header', you also have to call 'end_headers'
        self.end_headers()

        # Writing the HTML contents with UTF-8
        html = renderer.render_single_file(self.path)
        self.wfile.write(bytes(html, "utf8"))
        print("DEVEL GET")
        return


class ProdHTTPEventHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.path = f"/rendered/{self.path}"
        http.server.SimpleHTTPRequestHandler.do_GET(self)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", default="./site", help="Site input folder")
    parser.add_argument("-p", "--port", default=8080, help="Port for server", type=int)
    parser.add_argument("-d", "--debug", default=False, help="Whether to run in debug (on-the-fly rendering) or production mode", action="store_true")
    return parser.parse_args()

def main():
    args = parse_args()
    renderer.SITE_DIR = args.input
    renderer.setup('templates/')
    if not args.debug:
        renderer.generate_site()
    handler = DebugHTTPEventHandler if args.debug else ProdHTTPEventHandler
    with socketserver.TCPServer(("", args.port), handler) as httpd:
        print(f"Web server started at http://localhost:{args.port}")
        httpd.serve_forever() # Later add option to rerender without restarting script


if __name__ == "__main__":
    main()