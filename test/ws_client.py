import asyncio
import websockets

async def client():
    uri = "ws://localhost:10002"
    async with websockets.connect(uri) as websocket:
        # await websocket.send("Hello, server!")
        response = await websocket.recv()
        print(f"Received from server: {response}")

asyncio.run(client())