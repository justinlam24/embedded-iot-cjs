import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from flask_socketio import SocketIO
import random
import requests, time

app = Flask(__name__, static_folder="static")
app.secret_key = "supersecretkey"  # For session management

socketio = SocketIO(app, cors_allowed_origins="*")

FIREBASE_DB = "https://candjs-bb4db-default-rtdb.europe-west1.firebasedatabase.app/"
USER_DATA_PATH = "userdetails.json"
TRICK_HISTORY_PATH = "postlist.json"
QUERY = "?orderBy=\"$key\"&limitToLast=1000"

VALID_TRICKS = {
    "Kickflip": "kickflip.gif",
    "Heelflip": "heelflip.gif",
    "Shuv It": "shuvit.gif",
    "Front shuv": "frontshuv.gif",
    "360 shuv it": "360shuvit.gif",
    "360 shuv": "360shuv.gif",
    "Ollie": "ollie.gif"
}

# ---- ROUTES ----

@app.route('/')
def home():
    global last_trick_name
    last_trick_name = None 
    if "username" in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        # Fetch user data from Firebase
        response = requests.get(FIREBASE_DB + USER_DATA_PATH + QUERY)
        if response.ok:
            users = response.json()
            for key, user in users.items():
                if user.get("username") == username and user.get("password") == password or username == "admin" and password == "admin":
                    session["username"] = username
                    global last_trick_name
                    last_trick_name = None
                    return redirect(url_for("dashboard"))
                else:
                    return render_template("login.html", error="Invalid username or password.")
        
        # Make up a fake user for now
        # if username == "admin" and password == "admin":
        #     session["username"] = username
        #     return redirect(url_for("dashboard"))
        
        # return render_template("login.html", error="Invalid username or password.")
    
    return render_template("login.html")

@app.route('/dashboard')
def dashboard():
    global last_trick_name
    last_trick_name = None
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", username=session["username"])

@app.route('/logout')
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        # Fetch existing users
        response = requests.get(FIREBASE_DB + USER_DATA_PATH)
        if response.ok:
            users = response.json()
            if username in users:
                return render_template("register.html", error="Username already exists.")

        # Register new user
        new_user = {"username": username, "password": password}
        requests.patch(FIREBASE_DB + USER_DATA_PATH, json=new_user)
        

        session["username"] = username  # Log them in immediately
        return redirect(url_for("dashboard"))

    return render_template("register.html")



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

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

last_trick_name = None

def generate_motion():
    global last_trick_name
    counter = 0
    while True:
        try:
            response = requests.get(FIREBASE_DB + TRICK_HISTORY_PATH + "?orderBy=\"$key\"&limitToLast=1")

            if response.ok:
                db_data = response.json()
                #print("Latest trick name:", last_trick_name)
                if db_data:
                    latest_entry = list(db_data.values())[-1]
                    trick_name = latest_entry.get("trick name", "").strip()

                    if trick_name and trick_name != last_trick_name:
                        print("New trick detected:", trick_name)
                        gif_filename = VALID_TRICKS.get(trick_name, None)

                        if gif_filename:
                            skateboard_data = {
                                "trick_name": trick_name,
                                "gif_url": f"/static/gifs/{gif_filename}"
                            }
                            socketio.emit('perform_trick', skateboard_data)
                            socketio.emit('update_timeline', {"trick": trick_name})

                        last_trick_name = trick_name
                        eventlet.sleep(5)
                    else:
                        counter += 1
                        if counter > 2:
                            print("No new tricks detected. Resetting...")
                            counter = 0
                            skateboard_data = {
                                "trick_name": "Waiting for Trick...",
                                "gif_url": f"/static/gifs/default.gif"
                            }
                            socketio.emit('perform_trick', skateboard_data)

                
                # generate a random trick
                # trick_name = random.choice(list(VALID_TRICKS.keys()))
                # gif_filename = VALID_TRICKS[trick_name]
                # skateboard_data = {
                #     "trick_name": trick_name,
                #     "gif_url": f"/static/gifs/{gif_filename}"
                # }
                # socketio.emit('perform_trick', skateboard_data)
                # #socketio.emit('update_timeline', {"trick": trick_name})
                # print("Generated random trick:", trick_name)

            else:
                print("Error fetching data from Firebase:", response.text)

        except requests.RequestException as e:
            print("Error connecting to Firebase:", e)

        #eventlet.sleep(3)
            

@socketio.on('connect')
def handle_connect():
    print("Client connected")
    eventlet.spawn(generate_motion)

if __name__ == '__main__':
    socketio.run(app, debug=True)
