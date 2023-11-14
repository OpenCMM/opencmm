import xml.etree.ElementTree as ET
import re
from datetime import datetime

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


def get_coordinates(root: ET.Element, ns: str):
    position_path = f".//{ns}Position"
    positions = root.findall(position_path)
    # init timestamp
    timestamp = datetime(1970, 1, 1, 0, 0, 0, 0)
    xyz = []
    for p in positions:
        xyz += [float(p.text)]
        _timestamp = timestamp_str_to_datetime(p.attrib["timestamp"])
        if timestamp < _timestamp:
            timestamp = _timestamp
    return {
        "value": xyz,
        "timestamp": timestamp,
    }


def is_last_chunk(raw_data):
    return raw_data.endswith("/MTConnectStreams>\n\r\n")


def get_namespace(element: ET.Element):
    m = re.match(r"\{.*\}", element.tag)
    return m.group(0) if m else ""


def extract_version_number(string):
    """Extracts the version number after `MTConnectStreams:` from a string.

    Args:
      string: A string containing the version number.

    Returns:
      A string containing the version number, or None if the version number could
      not be extracted.
    """

    match = re.search(
        r"{urn:mtconnect.org:MTConnectStreams:(?P<version>\d+\.\d+)}MTConnectStreams",
        string,
    )
    if match:
        return match.group("version")
    else:
        return None


def get_mtconnect_version(xml_string: str):
    root = ET.fromstring(xml_string)
    tag = root.tag
    return extract_version_number(tag)


def get_linelabel(root: ET.Element, ns: str):
    if ns == "{urn:mtconnect.org:MTConnectStreams:1.3}":
        linelabel = root.findall(f".//{ns}Line")[0]  # ver1.3
    else:
        linelabel = root.findall(f".//{ns}LineLabel")[1]
    line = linelabel.text
    timestamp = linelabel.attrib["timestamp"]
    return {
        "value": line,
        "timestamp": timestamp_str_to_datetime(timestamp),
    }


def timestamp_str_to_datetime(timestamp: str, decimal_places=3):
    original_datetime = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    unix_timestamp = original_datetime.timestamp()
    rounded_unix_timestamp = round(unix_timestamp, decimal_places)
    return datetime.fromtimestamp(rounded_unix_timestamp)


def get_path_feedrate(root: ET.Element, ns: str):
    axis_path_feedrate = root.findall(f".//{ns}PathFeedrate")[0]
    feedrate = axis_path_feedrate.text
    timestamp = axis_path_feedrate.attrib["timestamp"]
    return {
        "value": float(feedrate),
        "timestamp": timestamp_str_to_datetime(timestamp),
    }


def mtconnect_table_row_data(xml_string: str, process_id: int):
    root = ET.fromstring(xml_string)
    timestamp = datetime(1970, 1, 1, 0, 0)
    xyz = get_coordinates(root, get_namespace(root))
    line = get_linelabel(root, get_namespace(root))
    feedrate = get_path_feedrate(root, get_namespace(root))
    columns = [xyz, line, feedrate]
    for c in columns:
        if timestamp < c["timestamp"]:
            timestamp = c["timestamp"]
    x = xyz["value"][0]
    y = xyz["value"][1]
    z = xyz["value"][2]
    return (process_id, timestamp, x, y, z, line["value"], feedrate["value"])
