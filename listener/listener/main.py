import websockets
import asyncio
import requests
from listener import mt
import xml.etree.ElementTree as ET
import mysql.connector
import threading

# home
# server_url = "ws://192.168.10.132:81"
server_url = "ws://192.168.10.114:81"
# mobile
# server_url = "ws://192.168.228.54:81"

# mock
# server_url = "ws://localhost:8081"

chunk_size = 1024
# position_path = './/{urn:mtconnect.org:MTConnectStreams:2.0}Position'
position_path = ".//{urn:mtconnect.org:MTConnectStreams:1.3}Position"
xyz = None
initial_coordinate = (109.074, -15.028, -561.215)
final_coordinate = (105.042, -11.028, -568.215)
done = False
data_to_insert = []


async def receive_sensor_data():
    global data_to_insert
    async with websockets.connect(server_url) as websocket:
        print("receive_sensor_data(): connected")

        while not done:
            distance = await websocket.recv()
            (x, y, z) = xyz
            data_to_insert.append((x, y, z, float(distance)))


# ref. https://stackoverflow.com/questions/67734115/how-to-use-multithreading-with-websockets
def listen_sensor():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(receive_sensor_data())
    loop.close()


def contorl_streaming_status(mysql_config: dict):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(control_sensor(mysql_config))
    loop.close()


async def control_sensor(mysql_config: dict):
    streaming = False
    global done
    async with websockets.connect(server_url) as websocket:
        print("control_sensor(): connected")

        idx = 0
        while not done:
            idx += 1
            if not streaming and xyz is not None:
                # if not streaming and xyz is not None and initial_coordinate == xyz:
                print("ready to start streaming")
                await websocket.send("startStreaming")
                print("start streaming")
                streaming = True

            elif streaming and xyz is not None and idx == 40:
                # elif streaming and xyz is not None and final_coordinate == xyz:
                print("ready to stop streaming")
                await websocket.send("stopStreaming")
                # await websocket.send("deepSleep")
                print("stop streaming")
                streaming = False
                done = True
                combine_data(mysql_config)

            await asyncio.sleep(0.5)


def combine_data(mysql_config: dict):
    # Perform a bulk insert
    mysql_conn = mysql.connector.connect(**mysql_config, database="coord")
    mysql_cur = mysql_conn.cursor()

    mysql_cur.executemany(
        "INSERT INTO sensor(x, y, z, distance) VALUES (%s, %s, %s, %s)", data_to_insert
    )
    mysql_conn.commit()
    mysql_cur.close()
    mysql_conn.close()


def mtconnect_streaming_reader(interval: int):
    global xyz
    # demo
    # endpoint = f"https://demo.metalogi.io/current?path=//Axes/Components/Linear/DataItems/DataItem&interval={interval}"

    endpoint = f"http://192.168.0.19:5000/current?path=//Axes/Components/Linear/DataItems&interval={interval}"
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


def listener_start(mysql_config: dict, mtconnect_interval: int):
    thread1 = threading.Thread(target=listen_sensor)
    thread2 = threading.Thread(target=mtconnect_streaming_reader, args=((mtconnect_interval, )))
    thread3 = threading.Thread(target=contorl_streaming_status, args=((mysql_config, )))

    # Start the threads
    thread1.start()
    thread2.start()
    thread3.start()

    # Join the threads (optional, to wait for them to finish)
    thread1.join()
    thread2.join()
    thread3.join()
