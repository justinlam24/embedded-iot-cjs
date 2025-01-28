import paho.mqtt.client as mqtt
import ssl

# Callback when the client connects to the server
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully!")
        # Subscribe to the topic after connecting
        client.subscribe("IC.embedded/CJS")
    else:
        print(f"Failed to connect, return code {rc}")

# Callback when a message is received
def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} on topic: {msg.topic}")

# Callback for when a publish is complete
def on_publish(client, userdata, mid):
    print(f"Message published successfully with mid: {mid}")

# Initialize MQTT client
client = mqtt.Client()

# Set TLS/SSL credentials
client.tls_set(
    ca_certs="mosquitto.org.crt",  # Path to the CA certificate
    certfile="client.crt",        # Path to the client certificate
    keyfile="client.key",         # Path to the client private key
    cert_reqs=ssl.CERT_REQUIRED,
    tls_version=ssl.PROTOCOL_TLSv1_2,
    ciphers=None
)

# Attach callback functions
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish

# Connect to the broker
try:
    client.connect("test.mosquitto.org", port=8884)
except Exception as e:
    print(f"Failed to connect to broker: {e}")
    exit(1)

# Start the loop in a separate thread to handle MQTT events
client.loop_start()

# Interactive message input
try:
    print("You can now type messages to send to the server. Type 'exit' to quit.")
    while True:
        message = input("Enter message: ")
        if message.lower() == "exit":
            print("Exiting...")
            break
        # Publish the message to the topic
        msg_info = client.publish("IC.embedded/CJS", message)
        if msg_info.rc == mqtt.MQTT_ERR_SUCCESS:
            print("Message queued successfully!")
        else:
            print(f"Error queuing message: {mqtt.error_string(msg_info.rc)}")
finally:
    client.loop_stop()
    client.disconnect()
    print("Disconnected from the server.")
