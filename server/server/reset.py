import mysql.connector
from server.config import MYSQL_CONFIG


def reset_tables():
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()

    query = """
		TRUNCATE `point`;
		TRUNCATE `line`;
		TRUNCATE `arc`;
	"""
    cursor.execute(query, multi=True)
    cnx.commit()

    cursor.close()
    cnx.close()
