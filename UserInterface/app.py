import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO
import random

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

def readfromFirebase():
    # Code to read data from Firebase
    return data


# Define skateboard tricks with rotation sequences
SKATEBOARD_TRICKS = [
    {"name": "Kickflip", "rotation_x": 2.0, "rotation_y": 0.0, "rotation_z": 0.5},   # Fast X-axis flip
    {"name": "Heelflip", "rotation_x": -2.0, "rotation_y": 0.0, "rotation_z": 0.5},  # Fast X-axis flip in opposite direction
    {"name": "Ollie", "rotation_x": 0.5, "rotation_y": 1.0, "rotation_z": 0.0},      # Small X flip, more Y-axis height
    {"name": "Pop Shove-it", "rotation_x": 0.0, "rotation_y": 0.0, "rotation_z": 3.0},  # Z-axis spin (shove-it effect)
    {"name": "Frontside 180", "rotation_x": 0.0, "rotation_y": 2.0, "rotation_z": 0.0},  # Big Y-axis spin
    {"name": "Backside 180", "rotation_x": 0.0, "rotation_y": -2.0, "rotation_z": 0.0},  # Reverse Y-axis spin
    {"name": "Impossible", "rotation_x": 3.0, "rotation_y": 1.0, "rotation_z": 1.0},  # Complex X, Y, and Z spin
    {"name": "Varial Kickflip", "rotation_x": 2.0, "rotation_y": 0.0, "rotation_z": 2.0},  # Kickflip + Shove-it
    {"name": "Hardflip", "rotation_x": 2.0, "rotation_y": 1.5, "rotation_z": 0.5},  # Kickflip + Frontside 180
    {"name": "Tre Flip", "rotation_x": 3.0, "rotation_y": 1.0, "rotation_z": 3.0}  # 360 Flip (Kickflip + 360 Shove-it)
]


def generate_motion():
    """Generate skateboard trick data every 5 seconds."""
    while True:
        eventlet.sleep(5)  # Wait before performing a new trick

        trick = random.choice(SKATEBOARD_TRICKS)  # Choose a random trick

        skateboard_data = {
            "trick_name": trick["name"],
            "rotation_x": trick["rotation_x"],
            "rotation_y": trick["rotation_y"],
            "rotation_z": trick["rotation_z"]
        }

        print(f"Performing Trick: {trick['name']}")  # Debug log
        socketio.emit('perform_trick', skateboard_data)  # Send data to frontend

@socketio.on('connect')
def handle_connect():
    print("Client connected")
    eventlet.spawn(generate_motion)  # Start sending trick data

if __name__ == '__main__':
    socketio.run(app, debug=True)
