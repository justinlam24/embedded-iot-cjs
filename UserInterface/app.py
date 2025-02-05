import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO
import random
import requests, time

app = Flask(__name__)
app.secret_key = "supersecretkey"  # For session management
socketio = SocketIO(app, cors_allowed_origins="*")

FIREBASE_DB = "https://candjs-bb4db-default-rtdb.europe-west1.firebasedatabase.app/"
USER_DATA_PATH = "users.json"
TRICK_HISTORY_PATH = "postlist.json"

VALID_TRICKS = {
    "Kickflip": "kickflip.gif",
    "Heelflip": "heelflip.gif",
    "Shuv it": "shuvit.gif",
    "Front shuv": "frontshuv.gif",
    "360 shuv it": "360shuvit.gif",
    "360 shuv": "360shuv.gif",
    "Ollie": "ollie.gif"
}

# ---- ROUTES ----

@app.route('/')
def home():
    if "username" in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        # Fetch user data from Firebase
        # response = requests.get(FIREBASE_DB + USER_DATA_PATH)
        # if response.ok:
        #     users = response.json()
        #     if username in users and users[username]["password"] == password:
        #         session["username"] = username
        #         return redirect(url_for("dashboard"))
        # Make up a fake user for now
        if username == "admin" and password == "admin":
            session["username"] = username
            return redirect(url_for("dashboard"))
        
        return render_template("login.html", error="Invalid username or password.")
    
    return render_template("login.html")

@app.route('/dashboard')
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", username=session["username"])

@app.route('/logout')
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route('/get_timeline')
def get_timeline():
    """Fetch the last 10 tricks for the logged-in user."""
    if "username" not in session:
        return jsonify([])

    response = requests.get(FIREBASE_DB + TRICK_HISTORY_PATH + "?orderBy=\"$key\"&limitToLast=10")
    if response.ok:
        moves = list(response.json().values())
        return jsonify(moves[::-1])  # Reverse order (newest first)
    return jsonify([])

def generate_motion():
    """Fetch the latest trick from Firebase and send it to the frontend only when it changes."""
    last_trick_name = None

    while True:
        eventlet.sleep(2)
        response = requests.get(FIREBASE_DB + TRICK_HISTORY_PATH + "?orderBy=\"$key\"&limitToLast=1")

        if response.ok:
            db_data = response.json()
            latest_data = list(db_data.values())[-1]
            # trick_name = latest_data.get("trick name", "").strip()

            # if trick_name and trick_name != last_trick_name:
            #     gif_filename = VALID_TRICKS.get(trick_name, None)

            #     if gif_filename:
            #         skateboard_data = {
            #             "trick_name": trick_name,
            #             "gif_url": f"/static/gifs/{gif_filename}"
            #         }
            #         socketio.emit('perform_trick', skateboard_data)
            #     last_trick_name = trick_name

            # random trick
            trick_name = random.choice(list(VALID_TRICKS.keys()))
            gif_filename = VALID_TRICKS.get(trick_name, None)
            skateboard_data = {
                "trick_name": trick_name,
                "gif_url": f"/static/gifs/{gif_filename}"
            }
            socketio.emit('perform_trick', skateboard_data)
            

@socketio.on('connect')
def handle_connect():
    print("Client connected")
    eventlet.spawn(generate_motion)

if __name__ == '__main__':
    socketio.run(app, debug=True)
