from server.config import MYSQL_CONFIG
from server.listener.mt import mtconnect_streaming_reader

def test_mtconnect_streaming_reader():
	# mtconnect_url = (
	# 	"http://192.168.0.19:5000/current?path=//Axes/Components/Linear/DataItems"
	# )
	mtconnect_url = (
	    "https://demo.metalogi.io/current?path=//Axes/Components/Linear/DataItems/DataItem"
	)

	interval = 200
	mtconnect_config = (mtconnect_url, interval)
	mtconnect_streaming_reader(mtconnect_config, MYSQL_CONFIG, 1)