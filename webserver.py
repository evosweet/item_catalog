from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from restaurantmod import get_all, edit, rec_update, new, add_rest
import cgi
import re
import urlparse


class webserverHandler(BaseHTTPRequestHandler):
    """ basic python web server """

    index = """
        <html>
            <body>
                <h1> this is a test <h2>
            </body>
        </html>
    """
  

    def do_GET(self):
        """ main get method """
        try:
            if self.path.endswith("/restaurants"):
                self.wfile.write(get_all())
            elif self.path.endswith("/edit"):
                rec_id = str(self.path).split("/")
                self.wfile.write(edit(rec_id[2]))
            elif self.path.endswith("/delete"):
                self.wfile.write("this is a test")
            elif self.path.endswith("/new"):
                self.wfile.write(new())
            else:
                self.send_error(404, "Path Not Found %s" % self.path)
        except:
            pass

    def do_POST(self):
        try:
            self.send_response(301)
            self.end_headers()
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                feilds = cgi.parse_multipart(self.rfile, pdict)
                if self.path.endswith('/edit'):
                    rec_id = feilds.get('id')
                    new_name = feilds.get('name')
                    return_id = rec_update(rec_id[0], new_name[0])
                    self.wfile.write(edit(return_id))
                elif self.path.endswith('new'):
                    new_name = feilds.get('name')
                    add_rest(new_name[0])
                    self.wfile.write(new())
                else:
                    self.send_error(404, "Path Not Found %s" % self.path)
        except:
            pass



def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webserverHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print "^C entered, stopping web server..."
        server.socket.close()


if __name__ == '__main__':
    main()
