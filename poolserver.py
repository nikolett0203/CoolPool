import sys # for argv
import os # for checking if svg file exists
import cgi # for parsing form data from shoot
import Physics
import json
import gzip
import random

from http.server import HTTPServer, BaseHTTPRequestHandler

from urllib.parse import urlparse, parse_qsl;

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

class MyHandler (BaseHTTPRequestHandler): 

    first = 0
    current = None
    high = None
    low = None
    p1_hilo = ""
    p2_hilo = ""
    player1 = None
    player2 = None
    game_name = None
    prev_hi_len = 7
    prev_lo_len = 7
    low_balls = [1,2,3,4,5,6,7]
    high_balls = [9,10,11,12,13,14,15]
    game = None
    table = None
    gameover = False
    winner = ""
    loser = ""

    last_svg =  """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
                <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
                "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
                <svg width="700" height="1375" viewBox="-25 -25 1400 2750"
                xmlns="http://www.w3.org/2000/svg"
                xmlns:xlink="http://www.w3.org/1999/xlink">
                <rect width="1350" height="2700" x="0" y="0" fill="#C0D0C0" /> 
                <rect width="1400" height="25" x="-25" y="-25" fill="darkgreen" />
                <text x="50%" y="50%" text-anchor="middle" font-family="Trebuchet MS" font-size="150" fill="green">GAME OVER!</text>
                <rect width="1400" height="25" x="-25" y="2700" fill="darkgreen" />
                <rect width="25" height="2750" x="-25" y="-25" fill="darkgreen" />
                <rect width="25" height="2750" x="1350" y="-25" fill="darkgreen" />
                <circle cx="0" cy="0" r="114" fill="black" />
                <circle cx="0" cy="1350" r="114" fill="black" />
                <circle cx="0" cy="2700" r="114" fill="black" />
                <circle cx="1350" cy="0" r="114" fill="black" />
                <circle cx="1350" cy="1350" r="114" fill="black" />
                <circle cx="1350" cy="2700" r="114" fill="black" />
                </svg>"""

    def do_GET(self):

        # breaks apart url into named tuple so you can extract individual 
        # components like protocol, domain name, path, etc.
        urlBits = urlparse(self.path)
        filepath = '.' + urlBits.path

        # use regex to determine if url contains table-?.svg
        # print(match = re.match('table-(\d+)\.svg', urlBits.path))

        # check if client's url includes path to our shoot file
        if urlBits.path in ['/index.html']:
            try:
                # retreive the HTML file by opening the file located in the 
                # current directory (.) with the client's requested resource
                # tacked onto the end
                with open(filepath, 'r') as fp:
                # fp = open('.' + self.path)
                    resource = fp.read()

                # send client 200 to indicate resource was found
                # send other info to browser about resource length and type
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.send_header("Content-length", len(resource))
                self.end_headers()

                # wfile ("write file") is the output stream for writing response 
                # back to client. We get it from the http.server module. 
                # The bytes and utf-8 line converts content from string to utf-8 bytes
                # because write expects bytes 
                self.wfile.write(bytes(resource, "utf-8"))
                fp.close()

            except FileNotFoundError:
                self.send_error(404, "File Not Found: %s" % self.path)

        elif urlBits.path in ['/play.html']:
            # get data from previous html form submission
            form_data = dict(parse_qsl(urlBits.query))

            # save form data
            MyHandler.player1 = form_data.get('player1', None)
            MyHandler.player2 = form_data.get('player2', None)
            MyHandler.game_name = form_data.get('game_name', None)

            # set up game and database
            MyHandler.game = Physics.Game(gameName=MyHandler.game_name, player1Name=MyHandler.player1, player2Name=MyHandler.player2)
            MyHandler.table = MyHandler.game.initialiseTable()

            # create first svg
            svg = MyHandler.table.svg()

            # determine player
            current = random.randint(1,2)

            # get html file
            with open('.' + urlBits.path, 'r') as fp:
                content = fp.read()

            # xml and doctype removed because unnecessary when svg is embedded directly into html
            svg_content = svg.split('\n', 2)[-1]  # This attempts to skip the XML/DOCTYPE lines

            # add form and svg content
            content = content.replace('%SVG_CONTENT%', svg_content)
            content = content.replace('%P1%', MyHandler.player1)
            content = content.replace('%P1_COUNT%', "7")
            content = content.replace('%P2%', MyHandler.player2)
            content = content.replace('%P2_COUNT%', "7")

            # randomly determine who plays first
            if (current == 1):
                content = content.replace('%CURRENT%', "Next shot: " + MyHandler.player1)
            else:
                content = content.replace('%CURRENT%', "Next shot: " + MyHandler.player2)                

            self.send_response(200)  # OK
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(content.encode('utf-8')) 

        elif urlBits.path.endswith('.css'):

            try:

                with open(filepath) as fp:
                    resource = fp.read()

                self.send_response(200)
                self.send_header("Content-type", "text/css")
                self.send_header("Content-length", len(resource))
                self.end_headers()

                self.wfile.write(bytes(resource, "utf-8"))

            except FileNotFoundError:
                self.send_error(404, "File Not Found: %s" % self.path)

        elif urlBits.path.endswith('.png'):

            try:
                with open(filepath, 'rb') as fp:
                    resource = fp.read()

                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.send_header('Content-length', len(resource))
                self.end_headers()

                self.wfile.write(resource)
            except FileNotFoundError:
                self.send_error(404, "File Not Found: %s" % self.path)

        else:
            # generate 404 for GET requests that aren't the 3 files above
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("404: %s not found" % self.path, "utf-8" ))

    def write_svg(self, table_id, table):
        return table.svg()

    def assign_hilo(self, firstBall):

        print(firstBall)

        if 1 <= firstBall <= 7:
            if MyHandler.current == 1:
                MyHandler.low = 1
                MyHandler.high = 2
                # MyHandler.p1_balls = list(range(1,8))
                # MyHandler.p2_balls = list(range(9, 16))
                MyHandler.p1_hilo = " (low)"
                MyHandler.p2_hilo = " (high)"
                print("here1")
            else: 
                # MyHandler.p2_balls = list(range(1,8))
                # MyHandler.p1_balls = list(range(9, 16))
                MyHandler.low = 2
                MyHandler.high = 1
                MyHandler.p2_hilo = " (low)"
                MyHandler.p1_hilo = " (high)"
                print("here2")
        else:
            if MyHandler.current == 1:
                MyHandler.low = 2
                MyHandler.high = 1
                # MyHandler.p1_balls = list(range(9, 16))
                # MyHandler.p2_balls = list(range(1,8))
                MyHandler.p2_hilo = " (low)"
                MyHandler.p1_hilo = " (high)"
                print("here3")
                # WORKS
            else:
                MyHandler.low = 1
                MyHandler.high = 2
                # MyHandler.p2_balls = list(range(9, 16))
                # MyHandler.p1_balls = list(range(1,8))
                MyHandler.p1_hilo = " (low)"
                MyHandler.p2_hilo = " (high)"
                print("here4")
                # WORKS!!!

        print(MyHandler.low, MyHandler.high)

    def game_state(self, low_left, high_left, eight):

        #p2 sunk b4 assignment and p1 won
        #p1 sunk b4 assignment and p2 won

        if MyHandler.current == MyHandler.low:
            if not eight:
                if not low_left:
                    MyHandler.gameover = True
                    MyHandler.winner = MyHandler.current
                    MyHandler.loser = 2 if MyHandler.current == 1 else 1
                    return True # game over
                    # 
                else:
                    MyHandler.gameover = True
                    MyHandler.loser = MyHandler.current
                    MyHandler.winner = 2 if MyHandler.current == 1 else 1
                    return True # game over  
                    # WORKS!
                
        elif MyHandler.current == MyHandler.high:
            if not eight:
                if not high_left:
                    MyHandler.gameover = True
                    MyHandler.winner = MyHandler.current
                    MyHandler.loser = 2 if MyHandler.current == 1 else 1
                    return True # game over 
                    # WORKS
                else:
                    MyHandler.gameover = True
                    MyHandler.loser = MyHandler.current
                    MyHandler.winner = 2 if MyHandler.current == 1 else 1
                    return True # game over 
                    # WORKS 
        else:
            if not eight:
                MyHandler.gameover = True
                MyHandler.loser = MyHandler.current
                MyHandler.winner = 2 if MyHandler.current == 1 else 1                                   

        return False



    def do_POST(self):

        if self.path == '/shoot!':

            # decode shot data from webpage
            length = int(self.headers['Content-Length'])
            data = self.rfile.read(length)
            decode = data.decode('utf-8')
            obj = json.loads(decode)

            # get coordinates
            vX = obj['velX']
            vY = obj['velY']

            # take the shot
            shotID, firstBall = self.game.shoot(MyHandler.game_name, MyHandler.player1, MyHandler.table, vX, vY);
            svg_frames, MyHandler.table = self.game.getShotTables(shotID)

            if firstBall is not None:
                print(firstBall)
                self.assign_hilo(firstBall)
                MyHandler.first = 1       

            MyHandler.table, MyHandler.low_balls, MyHandler.high_balls, eight = MyHandler.table.replace_cue_find_sunk(MyHandler.table.time)

            self.game_state(MyHandler.low_balls, MyHandler.high_balls, eight)

            # if balls have been assigned
            if MyHandler.first == 1:
            # switch players if no balls of own sunk
                if MyHandler.current == MyHandler.low:
                    if MyHandler.prev_lo_len == len(MyHandler.low_balls):
                        MyHandler.current = 2 if MyHandler.current == 1 else 1
                        print("here 10")
                    # hit none of p1 balls and switched
                        
                elif MyHandler.current == MyHandler.high:
                    if MyHandler.prev_hi_len == len(MyHandler.high_balls):
                        MyHandler.current = 2 if MyHandler.current == 1 else 1  
                        print("here 11")
                    # hit none of p2 balls and switched
            else:
                # if balls not assigned yet, just switch normally
                MyHandler.current = 2 if MyHandler.current == 1 else 1  
                print("here 12", MyHandler.current)
                # PLAYER 1 HIT PLAYER 2 BALL AND IT SUNK

            MyHandler.prev_lo_len = len(MyHandler.low_balls)         
            MyHandler.prev_hi_len = len(MyHandler.high_balls) 

            svg_frames.append(MyHandler.table.svg())

            if MyHandler.gameover:
                svg_frames.append(MyHandler.last_svg)

            svg_frames_json = json.dumps(svg_frames)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Encoding", "gzip")
            self.end_headers()
            compressed_data = gzip.compress(svg_frames_json.encode('utf-8'))
            self.wfile.write(compressed_data)
            print("Sent data length:", len(compressed_data))

        if self.path == '/stats':

            print("got it")

            if(MyHandler.gameover):
                if MyHandler.winner == 1:
                    data = "Congrats " + MyHandler.player1 + "! You won!"
                else:
                    data = "Congrats " + MyHandler.player2 + "! You won!"
            else:
                if (MyHandler.current == 1):
                    data = "Next shot:   " + MyHandler.player1 + MyHandler.p1_hilo
                    print(data)
                    
                else:
                    data = "Next shot:   " + MyHandler.player2 + MyHandler.p2_hilo 
                    print(data)

            print(len(MyHandler.low_balls))

            if MyHandler.low == 1:
                p1_balls = str(len(MyHandler.low_balls))
                p2_balls = str(len(MyHandler.high_balls))
            else:
                p1_balls = str(len(MyHandler.high_balls))
                p2_balls = str(len(MyHandler.low_balls))

            response_data = {
                'data': data,
                'p1': MyHandler.player1,
                'p1_count': p1_balls,
                'p2': MyHandler.player2,
                'p2_count': p2_balls,               
            }

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))              
            print("get it")

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("404: %s not found" % self.path, "utf-8" ))            

# check if program is being run directly or if it's imported
# if run directly, this code will execute
# if __name__ == "__main__":
    # create instance of HTTPServer class, makes server address as tuple
    # containing 'localhost' as the hostname and port number
    # MyHandler is the request handling class
    # httpd = HTTPServer(('localhost', int(sys.argv[1])), MyHandler)
    # print("Server listing in port:  ", int(sys.argv[1]))
    # # let server listen to request indefinitely using serve_forever method
    # httpd.serve_forever()

if __name__ == "__main__":
    httpd = HTTPServer(('0.0.0.0', PORT), MyHandler)
    print(f"Server listening on port {PORT}...")
    httpd.serve_forever()