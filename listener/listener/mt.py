import requests
import xml.etree.ElementTree as ET

# endpoint = "http://192.168.0.19:5000/current?path=//Axes/Components/Linear/DataItems&interval=2000"
# endpoint = "https://demo.metalogi.io/sample?path=//Axes/Components/Linear/DataItems/DataItem[@id=%22Xpos%22]&interval=1000"
endpoint = "https://demo.metalogi.io/sample?path=//Axes/Components/Linear/DataItems/DataItem&interval=1000"
# endpoint = "https://demo.metalogi.io/sample?path=//Axes/Components/Linear[@id=%22x%22]&interval=0"
# endpoint = "https://demo.metalogi.io/current?path=//DataItems/DataItem[@id=%22avail%22]&interval=2000"

response = requests.get(endpoint, stream=True)
xml_start = '<?xml version="1.0" encoding="UTF-8"?>'


def remove_http_response_header(res: str):
    xml_str = res[res.find(xml_start) :]
    return xml_str


def is_first_chunk(raw_data: str) -> bool:
    """
    Each section of the document begins with a boundary preceded by two hyphens (--).
    ref. https://model.mtconnect.org/#Package__8082e379-d82e-4b0e-abad-83cdf92f7fe6
    """
    # get the first two letters of the string
    two = raw_data[:2]
    return two == "--"


def get_coordinates(xml_string: str, position_path: str):
    root = ET.fromstring(xml_string)
    positions = root.findall(position_path)
    xyz = tuple([float(p.text) for p in positions])
    return xyz


def is_last_chunk(raw_data):
    return raw_data.endswith("/MTConnectStreams>\n\r\n")
