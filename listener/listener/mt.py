import xml.etree.ElementTree as ET
import re

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


def get_coordinates(xml_string: str):
    root = ET.fromstring(xml_string)
    version = get_mtconnect_version(xml_string)
    position_path = ".//{urn:mtconnect.org:MTConnectStreams:" + version + "}Position"
    positions = root.findall(position_path)
    xyz = tuple([float(p.text) for p in positions])
    return xyz


def is_last_chunk(raw_data):
    return raw_data.endswith("/MTConnectStreams>\n\r\n")

def extract_version_number(string):
  """Extracts the version number after `MTConnectStreams:` from a string.

  Args:
    string: A string containing the version number.

  Returns:
    A string containing the version number, or None if the version number could
    not be extracted.
  """

  match = re.search(r'{urn:mtconnect.org:MTConnectStreams:(?P<version>\d+\.\d+)}MTConnectStreams', string)
  if match:
    return match.group('version')
  else:
    return None

def get_mtconnect_version(xml_string: str):
    root = ET.fromstring(xml_string)
    tag = root.tag
    return extract_version_number(tag)