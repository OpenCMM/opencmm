import websockets
import asyncio


# start a websocket server and receive data from the client
async def server(websocket):
    idx = 0
    image_data = b""
    waiting_image = False
    while True:
        # read console input
        if not waiting_image:
            message = input("Enter message: ")
            await websocket.send(message) 
            waiting_image = True

        data = await websocket.recv()
        if isinstance(data, bytes):
            # concatenate the image data
            image_data += data

        elif isinstance(data, str):
            if data == "end":
                # save as image
                with open(f"{idx}.jpg", "wb") as f:
                    f.write(image_data)
                    print(f"Saved image {idx}.jpg")
                    idx += 1
                    image_data = b""
                
                waiting_image = False

            else:
                print(f"Received: {data}")


# start the server
start_server = websockets.serve(server, "192.168.10.110", 8765)

# run the server
asyncio.get_event_loop().run_until_complete(start_server)

# keep the server running
asyncio.get_event_loop().run_forever()
