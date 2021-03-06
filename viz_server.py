#!/usr/bin/env python
import os
import argparse
import mimetypes

from http.server import BaseHTTPRequestHandler, HTTPServer

TEMPLATE = """
<!DOCTYPE HTML>
<html>

<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>Halite Visualizer</title>

    <link href="/lib/bootstrap.min.css" rel="stylesheet">
</head>

<body onload="init_vis();">
    <div id="container" class="container">
        <div id="pageContent" class="pageContent text-center"></div>
    </div>

    <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.2.4/jquery.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/seedrandom/2.4.0/seedrandom.min.js"></script>
    <script src="/lib/xss.js"></script>
    <script src="/lib/pixi.min.js"></script>
    <script src="/script/parsereplay.js"></script>
    <script src="/script/visualizer.js"></script>

    <script type="text/javascript">
        function init_vis() {
            var replay_data = 'REPLAY_DATA';
            var game = textToGame(replay_data, 'FILENAME');
            showGame(game, $("#pageContent"), null, null, true, false, true);
        }
    </script>
</body>

</html>
"""


def make_replay(filename):
    html = "File not found"
    if os.path.exists(filename):
        with open(filename) as f:
            replay_data = f.read()
        html = TEMPLATE.replace("FILENAME", filename)
        html = html.replace("REPLAY_DATA", replay_data)
    return html


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/r/'):
            message = make_replay(os.path.join(REPLAYS_DIR, self.path[3:]) + '.hlt')
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(bytes(message, 'utf8'))
        elif self.path == '/':
            files = os.listdir(REPLAYS_DIR)
            files = [f[:-4] for f in files if f.endswith('.hlt')]
            html = ['<a href="/r/{}">{}</a>'.format(f, f) for f in files]
            message = '\n'.join(html)
            message = '<!DOCTYPE HTML><html><body>' + message + '</body></html>'
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(bytes(message, 'utf8'))
        else:
            fname = self.path[1:]
            if os.path.exists(fname):
                self.send_response(200)
                # print( mimetypes.guess_type(fname, strict=False))
                self.send_header('Content-type', mimetypes.guess_type(fname, strict=False)[0])
                self.end_headers()
                with open(fname, 'rb') as f:
                    self.wfile.write(f.read())

    def log_message(self, format, *args):
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default=8081, type=int,
                        help='Specify alternate port [default: 8081]')
    parser.add_argument('path', action='store', help='Directory containing replay files')
    args = parser.parse_args()

    REPLAYS_DIR = args.path

    print('Serving replays at {} on port {}'.format(REPLAYS_DIR, args.port))
    server_address = ('localhost', args.port)
    httpd = HTTPServer(server_address, Handler)
    httpd.serve_forever()
