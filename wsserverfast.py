import socketio

# Create a Socket.IO client
sio = socketio.Client()

# Event handler for connecting to the server
@sio.event
def connect():
    print("Connected to the server!")
    sio.send("Hello Server!")

# Event handler for receiving a message
@sio.event
def message(data):
    print(f"Message from server: {data}")

# Event handler for disconnecting from the server
@sio.event
def disconnect():
    print("Disconnected from the server!")

# Connect to the Socket.IO server
sio.connect('http://localhost:5000')

# Keep the client running to handle events
sio.wait()
