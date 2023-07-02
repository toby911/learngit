import websockets
import uuid
import asyncio
import requests

class websocketServer():
    def __init__(self, server_ip, server_port) -> None:
        self.clients_dict = {}
        self.server_ip = server_ip
        self.server_port = server_port
        
    async def send_data(self, client_id, data):
        if client_id in self.clients_dict:
            await self.clients_dict[client_id].send(data)
            return {'data': "websocket send data success"}
        else:
            return {'data': "failed: No such websocket connection"}
        
    def websockets_server(self):
        async def server(websocket, path):
            client_id = str(uuid.uuid4())
            self.clients_dict[client_id] = websocket
            print(websocket.state)
            while True:
                try:
                    message = await websocket.recv()
                    print(message)
                    print(self.clients_dict)
                    await self.clients_dict[client_id].send(client_id)
                except websockets.exceptions.ConnectionClosedError:
                    # del self.clients_dict[client_id]
                    continue
                
                except websockets.exceptions.ConnectionClosedOK:
                    # del self.clients_dict[client_id]
                    continue
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        start_server = websockets.serve(server, self.server_ip, self.server_port)
        loop.run_until_complete(start_server)
        loop.run_forever()
