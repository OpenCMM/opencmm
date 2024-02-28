#!/usr/bin/python3

"""
Capture an image with the raspberry pi high quality camera and send it to the server over websockets when it receives a message
"""

from picamera2 import Picamera2
import websockets
import asyncio
import time
import io
import sys
import argparse

def take_picture(picam2) -> bytes:
    data = io.BytesIO()
    picam2.capture_file(data, format="jpeg")
    image_data = data.getvalue()
    return image_data



async def main(is_full: bool = False):
    """
    Establishes a websocket connection and sends images to the server when prompted
    :param is_full: bool: True to use full mode, False to use preview mode
    """

    # establish the websockets connection
    uri = "ws://192.168.10.110:8765"
    async with websockets.connect(uri) as websocket:
        picam2 = Picamera2()
        if is_full:
            picam2.configure(picam2.create_still_configuration())
        else:
            picam2.configure(picam2.create_preview_configuration())
        picam2.start()
        print("camera started")

        time.sleep(1)

        idx = 0

        # print received message
        async for message in websocket:
            print(message)
            if message == "end":
                break

            # take a picture
            print(f"taking a picture - {idx}")
            image_data = take_picture(picam2)
            chunk_size = 1024  # Set the desired chunk size

            # Calculate the total number of chunks
            total_chunks = (len(image_data) + chunk_size - 1) // chunk_size
            await websocket.send(
                f"sending {total_chunks} chunks of data - {idx}"
            )

            # Send data in smaller chunks
            for i in range(total_chunks):
                start = i * chunk_size
                end = (i + 1) * chunk_size
                chunk = image_data[start:end]
                await websocket.send(chunk)
            await websocket.send("end")
            idx += 1

        picam2.stop()
        exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--full', action='store_true', help='Use full mode')
    args = parser.parse_args()

    is_full = args.full

    try:
        asyncio.run(main(is_full))
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
    finally:
        print("Exiting...")
        sys.exit(1)
