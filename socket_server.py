import socketio


sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, socketio_path="ws")

register_room = {}


@sio.event
async def connect(sid, environ):
    print(f'Cient connected: {sid}')

@sio.event
async def disconnect(sid):
    print(f'Client disconnected: {sid}')

@sio.event
async def join(sid, data):
    room = data.get('room')
    username = data.get('username')
    print(f'{username} is trying to join room: {room}')

    register_room[sid] = {"username": username, "room":room}

    await sio.enter_room(sid, room)
    print(f'{username} joined room: {room}')
    

@sio.event
async def live_message(sid, data):
    print(f'Message from {sid}: {data}')
    print(register_room[sid]['room'])
    await sio.emit("live_message", data, room=register_room[sid]['room'])
    print('message sent!')