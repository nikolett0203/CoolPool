from flask import Flask, url_for, redirect, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("new_game.html")

# @app.route("/<name>")
# def play(name):
#     return f"Hello {name}!"

# @app.route("/admin")
# def admin():
#     return redirect(url_for("play", name="admin!"))

if __name__ == "__main__":
    app.run(debug=True)