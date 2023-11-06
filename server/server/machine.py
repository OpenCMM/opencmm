import mysql.connector
import smbclient
from pydantic import BaseModel


class MachineInfo(BaseModel):
    machine_id: int
    ip: str
    username: str
    password: str
    shared_folder: str

    def __init__(self, machine_id, ip, username, password, shared_folder):
        super().__init__(
            machine_id=machine_id,
            ip=ip,
            username=username,
            password=password,
            shared_folder=shared_folder,
        )

    def __iter__(self):
        yield self.machine_id
        yield self.ip
        yield self.username
        yield self.password
        yield self.shared_folder


def get_machines(mysql_config: dict):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "SELECT * FROM machine"
    cursor.execute(query)
    machines = cursor.fetchall()
    cursor.close()
    cnx.close()
    return machines


def update_machine(mysql_config: dict, machine_info: MachineInfo):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = (
        "UPDATE machine SET ip = %s, username = %s,"
        "password = %s, shared_folder = %s WHERE id = %s"
    )
    machine_id, ip, username, password, shared_folder = machine_info
    cursor.execute(query, (ip, username, password, shared_folder, machine_id))
    cnx.commit()
    cursor.close()
    cnx.close()
    return True


def send_file_with_smbclient(machine_info: tuple, file_path: str):
    machine_id, ip, username, password, shared_folder = machine_info
    filename = get_filename_from_path(file_path)
    smbclient.ClientConfig(username=username, password=password)
    with smbclient.open_file(
        r"//{}/{}/{}".format(ip, shared_folder, filename),
        mode="w",
    ) as f:
        f.write(file_path)


def list_shared_folder_with_smbclient(machine_info: tuple):
    machine_id, ip, username, password, shared_folder = machine_info
    smbclient.ClientConfig(username=username, password=password)
    files = smbclient.listdir(r"//{}/{}".format(ip, shared_folder))
    return files


def delete_file_with_smbclient(machine_info: tuple, file_path: str):
    machine_id, ip, username, password, shared_folder = machine_info
    filename = get_filename_from_path(file_path)
    smbclient.ClientConfig(username=username, password=password)
    smbclient.unlink(r"//{}/{}/{}".format(ip, shared_folder, filename))
    files = smbclient.listdir(r"//{}/{}".format(ip, shared_folder))
    assert filename not in files


def get_filename_from_path(file_path: str):
    return file_path.split("/")[-1]
