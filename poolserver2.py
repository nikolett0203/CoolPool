from flask import Flask, url_for, redirect, render_template, request, session, Response, jsonify
import random
import Physics
import time
import json
import gzip

app = Flask(__name__)
app.secret_key = "hello"

games = {}

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":
        session['game_name'] = request.form.get("game_name")
        session['player1'] = request.form.get("player1")
        session['player2'] = request.form.get("player2")

        session_id = session.get('_id', str(random.randint(1000, 9999)))
        session['_id'] = session_id

        # Create a new Game instance
        games[session_id] = Physics.Game(gameName=session['game_name'],
                                         player1Name=session['player1'],
                                         player2Name=session['player2'])

        table = games[session_id].get_table()
        table_svg = table.svg()

        curr_player = session['player1'] if games[session_id].get_current() == '1' else session['player2']

        print("CURRENT1: ", curr_player)

        return render_template("play_game.html", 
                            player1=session['player1'], 
                            player2=session['player2'], 
                            p1_count=7,
                            p2_count=7,
                            current=curr_player,
                            lo_balls="Unassigned",
                            hi_balls="Unassigned",
                            svg_data=table_svg)

    return render_template("init_game.html")


@app.route("/play_game", methods=["GET", "POST"])
def play_game():

    if "player1" in session:
        return render_template("play_game.html")
    else:
        return redirect(url_for("home"))
    

@app.route('/shoot!', methods=['GET', 'POST'])
def shoot():

    if request.method == 'POST':

        # retrieve the velocity data from the client
        data = request.get_json()
        vel_x = data.get('velX')
        vel_y = data.get('velY')

        # get current game instance
        session_id = session['_id']
        game = games[session_id]
        svg_frames = game.game_logic(vel_x, vel_y)

        svg_frames_json = json.dumps(svg_frames)
        compressed_data = gzip.compress(svg_frames_json.encode('utf-8'))

        response = Response(compressed_data, content_type='application/json')
        response.headers['Content-Encoding'] = 'gzip'
        response.headers['Content-Length'] = str(len(compressed_data))
        response.headers['Vary'] = 'Accept-Encoding'

        return response

@app.route('/stats', methods=['GET', 'POST'])
def stats():

    if request.method == 'POST':

        session_id = session['_id']
        game = games[session_id]

        response_data = {}
    
        if game.get_gamestatus():
            pass
        else:

            response_data['player1'] = session['player1']
            response_data['player2'] = session['player2']

            print("CURRENT 2", game.get_currentplayer())

            if game.get_currentplayer() == 1:
                response_data['current'] = session['player1']
            else: 
                response_data['current'] = session['player2']

            response_data['lo_balls'] = game.get_low_assignment()
            response_data['hi_balls'] = game.get_high_assignment()

            assmt = game.get_assignment()

            if assmt is None:
                response_data['p1_count'] = 7
                response_data['p2_count'] = 7
            elif assmt == 1:
                response_data['p1_count'] = game.get_highballs()
                response_data['p2_count'] = game.get_lowballs()
            else:
                response_data['p1_count'] = game.get_lowballs()
                response_data['p2_count'] = game.get_highballs()

        dump = json.dumps(response_data).encode('utf-8')
        response = Response(dump, content_type='application/json')

        return response
    
@app.route('/new_game', methods=['GET', 'POST'])
def new_game():
    session_id = session.get('_id')

    if session_id and session_id in games:
        del games[session_id]

    session.clear()

    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True, port=5004)







