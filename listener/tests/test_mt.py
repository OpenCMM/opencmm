import requests
from listener import mt
import xml.etree.ElementTree as ET

# endpoint = "https://demo.metalogi.io/sample?path=//Axes/Components/Linear/DataItems/DataItem[@id=%22Xpos%22]&interval=1000"
# endpoint = "https://demo.metalogi.io/sample?path=//Axes/Components/Linear/DataItems/DataItem&interval=1000"
# endpoint = "https://demo.metalogi.io/sample?path=//Axes/Components/Linear[@id=%22x%22]&interval=0"
# endpoint = "https://demo.metalogi.io/current?path=//DataItems/DataItem[@id=%22avail%22]&interval=2000"

position_path = ".//{urn:mtconnect.org:MTConnectStreams:2.0}Position"


def test_remove_http_respose_header():
    endpoint = "https://demo.metalogi.io/sample?path=//Axes/Components/Linear/DataItems/DataItem&interval=1000"
    idx = 0

    try:
        response = requests.get(endpoint, stream=True)
        xml_buffer = ""
        if response.status_code == 200:
            for chunk in response.iter_content(chunk_size=1024):
                raw_data = chunk.decode("utf-8")
                if idx > 100:
                    raise ET.ParseError("ParseError")

                if mt.is_first_chunk(raw_data):
                    # beginning of xml
                    xml_string = mt.remove_http_response_header(raw_data)
                    xml_buffer = xml_string

                    if mt.is_last_chunk(raw_data):
                        try:
                            xyz = mt.get_coordinates(xml_buffer, position_path)[:3]
                            for v in xyz:
                                assert v is not None
                                # check if the values are float
                                assert isinstance(v, float)
                            break
                        except ET.ParseError:
                            pass
                else:
                    xml_buffer += raw_data
                    if not mt.is_last_chunk(raw_data):
                        continue

                    # full xml data received
                    try:
                        xyz = mt.get_coordinates(xml_buffer, position_path)[:3]
                        for v in xyz:
                            assert v is not None
                            # check if the values are float
                            assert isinstance(v, float)
                        break

                    except ET.ParseError:
                        raise ET.ParseError("ParseError")
                idx += 1

        else:
            print("Error:", response.status_code)

    except requests.ConnectionError:
        print("Connection to the MTConnect agent was lost.")
