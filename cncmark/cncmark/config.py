import os

# For github actions
CI_MYSQL_CONFIG = dict(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="root",
)


MYSQL_CONFIG = dict(
    host="raspberrypi.local",
    port=3306,
    user="yuchi",
    password="raspberrypi",
)

if os.environ.get("CI"):
    MYSQL_CONFIG = CI_MYSQL_CONFIG
