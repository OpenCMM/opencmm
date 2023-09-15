import websockets
import asyncio
import time

server_url = "ws://192.168.10.132:81"

async def listen():
    async with websockets.connect(server_url) as websocket:
        print("connected")
        await websocket.send("startStreaming")

        idx = 0
        start = time.time()
        total_time = 0

        while idx < 100:
            _start = time.time()

            with open("data.csv", "a") as f:
                distance = await websocket.recv()
                data = (*get_coordinate(), distance)
                f.write(",".join(map(str, data)) + "\n")
                idx += 1

            _end = time.time()
            total_time += _end - _start
        
        print(f"average time: {total_time / idx * 1000} ms")
        end = time.time()
        print(f"elapsed time: {end - start} sec")
        await websocket.send("stopStreaming")

def get_coordinate():
    # get coordinate from server
    return (0, 0, 0)

async def main():
    await listen()

if __name__ == "__main__":
    asyncio.run(main())