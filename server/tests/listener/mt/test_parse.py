import requests
from server.listener import mt
from server.listener.mt import parse
from datetime import datetime
import xml.etree.ElementTree as ET

# endpoint = "https://demo.metalogi.io/sample?path=//Axes/Components/Linear/DataItems/DataItem[@id=%22Xpos%22]&interval=1000"
# endpoint = "https://demo.metalogi.io/sample?path=//Axes/Components/Linear/DataItems/DataItem&interval=1000"
# endpoint = "https://demo.metalogi.io/sample?path=//Axes/Components/Linear[@id=%22x%22]&interval=0"
# endpoint = "https://demo.metalogi.io/current?path=//DataItems/DataItem[@id=%22avail%22]&interval=2000"


def test_remove_http_respose_header():
    endpoint = "https://demo.metalogi.io/current?path=//Components&interval=1000"
    idx = 0

    try:
        response = requests.get(endpoint, stream=True)
        xml_buffer = ""
        if response.status_code == 200:
            for chunk in response.iter_content(chunk_size=1024):
                raw_data = chunk.decode("utf-8")
                if idx > 100:
                    raise ET.ParseError("ParseError")

                if parse.is_first_chunk(raw_data):
                    # beginning of xml
                    xml_string = parse.remove_http_response_header(raw_data)
                    xml_buffer = xml_string

                    if parse.is_last_chunk(raw_data):
                        try:
                            row = parse.mtconnect_table_row_data(xml_buffer, 1)
                            xyz = row[2:5]
                            for v in xyz:
                                assert v is not None
                                # check if the values are float
                                assert isinstance(v, float)

                            timestamp = row[1]
                            assert timestamp is not None
                            assert isinstance(timestamp, datetime)

                            line = row[5]
                            assert line is not None
                            assert isinstance(line, str)

                            feedrate = row[6]
                            assert feedrate is not None
                            assert isinstance(feedrate, float)

                            break
                        except ET.ParseError:
                            pass
                else:
                    xml_buffer += raw_data
                    if not parse.is_last_chunk(raw_data):
                        continue

                    # full xml data received
                    try:
                        row = parse.mtconnect_table_row_data(xml_buffer, 1)
                        xyz = row[2:5]
                        for v in xyz:
                            assert v is not None
                            # check if the values are float
                            assert isinstance(v, float)

                        timestamp = row[1]
                        assert timestamp is not None
                        assert isinstance(timestamp, datetime)

                        line = row[5]
                        assert line is not None
                        assert isinstance(line, str)

                        feedrate = row[6]
                        assert feedrate is not None
                        assert isinstance(feedrate, float)

                        break

                    except ET.ParseError:
                        raise ET.ParseError("ParseError")
                idx += 1

        else:
            print("Error:", response.status_code)

    except requests.ConnectionError:
        print("Connection to the MTConnect agent was lost.")


def test_get_namespace():
    tree = ET.parse("tests/fixtures/xml/demo.xml")
    root = tree.getroot()
    ns = mt.get_namespace(root)
    assert ns == "{urn:mtconnect.org:MTConnectStreams:2.0}"


def test_devices():
    tree = ET.parse("tests/fixtures/xml/demo.xml")
    root = tree.getroot()
    ns = mt.get_namespace(root)
    device_stream_path = f".//{ns}DeviceStream"
    devices = root.findall(device_stream_path)
    assert len(devices) == 3


def test_get_linelabel():
    tree = ET.parse("tests/fixtures/xml/demo.xml")
    root = tree.getroot()
    ns = mt.get_namespace(root)
    linelabel_obj = parse.get_linelabel(root, ns)
    assert linelabel_obj["value"] == "10"
    assert linelabel_obj["timestamp"] == datetime(2023, 10, 31, 8, 11, 27, 497000)


def test_get_path_feedrate():
    tree = ET.parse("tests/fixtures/xml/demo.xml")
    root = tree.getroot()
    ns = mt.get_namespace(root)
    path_feedrate_obj = parse.get_path_feedrate(root, ns)
    assert path_feedrate_obj["value"] == 0.0
    assert path_feedrate_obj["timestamp"] == datetime(2023, 10, 31, 8, 11, 38, 10000)


def test_get_coordinates():
    tree = ET.parse("tests/fixtures/xml/demo.xml")
    root = tree.getroot()
    ns = mt.get_namespace(root)
    coordinates_obj = parse.get_coordinates(root, ns)
    assert coordinates_obj["value"][0] == 4773.5319
    assert coordinates_obj["timestamp"] == datetime(2023, 10, 31, 8, 11, 58, 311000)
