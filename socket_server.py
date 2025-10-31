import socketio


sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, socketio_path="ws")


cli_connections = {}


@sio.event
async def connect(sid, environ):
    print(f'Cient connected: {sid}')

@sio.event
async def disconnect(sid):
    print(cli_connections, "disconnecting room")
    if sid in cli_connections:
        del cli_connections[sid]
    print(cli_connections, "disconnected")
    print(f'Client disconnected: {sid}')


@sio.event
async def join(sid, data):
    room_data = data.get('room').split('-')

    room = room_data[1]
    if room_data[0] == "cli":
        if room in cli_connections.values():
            return {"status_code": 409, "message": "Pipeline already exists"}
        cli_connections[sid] = room

    await sio.enter_room(sid, room)
    print(cli_connections)
    return {"status_code": 200, "message": f"Joined room {room} successfully"}

    

@sio.event
async def live_message(sid, data):
    rooms_list = list(sio.rooms(sid))
    room = rooms_list[1]
    await sio.emit("live_message", data, room=room)
    print('message sent!')