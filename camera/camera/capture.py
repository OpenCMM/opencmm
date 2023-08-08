from camera.config import MYSQL_CONFIG
import mysql.connector
from mysql.connector.errors import IntegrityError


def add_img_path(img_path: str, point_id: str):
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()

    update_query = """
        UPDATE point
        SET img_path = %s
        WHERE point_id = %s
    """
    try:
        data = (img_path, point_id)
        cursor.execute(update_query, data)
    except IntegrityError:
        print("Error: unable to update points")

    cnx.commit()
    cursor.close()
    cnx.close()
