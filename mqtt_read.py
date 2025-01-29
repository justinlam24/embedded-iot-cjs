import paho.mqtt.client as mqtt

# Callback when the client connects to the server
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully!")
        client.subscribe("IC.embedded/CJS")  # Subscribe to topic
    else:
        print(f"Failed to connect, return code {rc}")

# Callback when a message is received
def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print(f"Received message: {message} from topic: {msg.topic}")
    if message == "Hello":
        print("What's good, how are you?")

# Initialize MQTT client
client = mqtt.Client()

# Attach callback functions
client.on_connect = on_connect
client.on_message = on_message

# Connect to broker (non-TLS for testing)
try:
    client.connect("test.mosquitto.org", port=1883)  # Non-TLS port
except Exception as e:
    print(f"Failed to connect to broker: {e}")
    exit(1)

# Start listening for messages
print("Listening for messages on topic 'IC.embedded/CJS'... Press Ctrl+C to exit.")
try:
    client.loop_forever()
except KeyboardInterrupt:
    print("\nExiting...")
    client.disconnect()
