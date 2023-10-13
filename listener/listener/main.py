import websockets
import asyncio
import sqlite3
import requests
from listener import mt
import xml.etree.ElementTree as ET
import threading

# home
# server_url = "ws://192.168.10.132:81"
server_url = "ws://192.168.10.114:81"
# mobile
# server_url = "ws://192.168.228.54:81"

# mock
# server_url = "ws://localhost:8081"

# usb
# th = 3950
# 3.7 battery
th = 3600

chunk_size = 1024
# position_path = './/{urn:mtconnect.org:MTConnectStreams:2.0}Position'
position_path = ".//{urn:mtconnect.org:MTConnectStreams:1.3}Position"
xyz = None
distance = None
initial_coordinate = (109.074, -15.028, -561.215)
final_coordinate = (105.042, -11.028, -568.215)
streaming = False
done = False


async def receive_sensor_data():
    global distance
    async with websockets.connect(server_url) as websocket:
        print("receive_sensor_data(): connected")

        while not done:
            distance = await websocket.recv()


# ref. https://stackoverflow.com/questions/67734115/how-to-use-multithreading-with-websockets
def listen_sensor():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(receive_sensor_data())
    loop.close()


def contorl_streaming_status():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(control_sensor())
    loop.close()


async def control_sensor():
    global streaming, xyz, done
    async with websockets.connect(server_url) as websocket:
        print("control_sensor(): connected")

        while not done:
            if not streaming and xyz is not None and initial_coordinate == xyz:
                print("ready to start streaming")
                await websocket.send("startStreaming")
                print("start streaming")
                streaming = True

            elif streaming and xyz is not None and final_coordinate == xyz:
                print("ready to stop streaming")
                await websocket.send("stopStreaming")
                # await websocket.send("deepSleep")
                print("stop streaming")
                streaming = False
                done = True

            await asyncio.sleep(0.5)


def combine_data():
    global xyz, distance
    conn = sqlite3.connect("listener.db")
    cur = conn.cursor()

    data_to_insert = []
    while not done:
        if distance is not None and xyz is not None:
            # Combine sensor_data and coordinate_data
            combined_data = (*xyz, float(distance))
            (x, y, z) = xyz
            print(combined_data)
            data_to_insert.append((x, y, z, float(distance)))
            # Reset the variables to wait for new data
            distance = None
            xyz = None

    # Perform a bulk insert
    cur.executemany(
        "INSERT INTO coord(x, y, z, distance) VALUES (?, ?, ?, ?)", data_to_insert
    )
    conn.commit()
    conn.close()


def mtconnect_streaming_reader():
    global xyz
    # demo
    # endpoint = "https://demo.metalogi.io/sample?path=//Axes/Components/Linear/DataItems/DataItem&interval=1000"

    endpoint = "http://192.168.0.19:5000/current?path=//Axes/Components/Linear/DataItems&interval=1000"
    try:
        response = requests.get(endpoint, stream=True)
        xml_buffer = ""
        if response.status_code == 200:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if not chunk:
                    continue
                if done:
                    break

                raw_data = chunk.decode("utf-8")
                # print(raw_data)
                if mt.is_first_chunk(raw_data):
                    # beginning of xml
                    xml_string = mt.remove_http_response_header(raw_data)
                    xml_buffer = xml_string

                    if mt.is_last_chunk(raw_data):
                        try:
                            xyz = mt.get_coordinates(xml_buffer, position_path)[:3]
                        except ET.ParseError:
                            pass
                else:
                    xml_buffer += raw_data
                    if not mt.is_last_chunk(raw_data):
                        continue

                    # full xml data received
                    try:
                        xyz = mt.get_coordinates(xml_buffer, position_path)[:3]

                    except ET.ParseError:
                        print("ParseError")

        else:
            print("Error:", response.status_code)

    except requests.ConnectionError:
        print("Connection to the MTConnect agent was lost.")
    except KeyboardInterrupt:
        print("Streaming stopped by user.")


if __name__ == "__main__":
    thread1 = threading.Thread(target=listen_sensor)
    thread2 = threading.Thread(target=mtconnect_streaming_reader)
    thread3 = threading.Thread(target=combine_data)
    thread4 = threading.Thread(target=contorl_streaming_status)

    # Start the threads
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()

    # Join the threads (optional, to wait for them to finish)
    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()
