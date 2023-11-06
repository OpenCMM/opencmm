from server.machine import (
    get_machines,
    update_machine,
    send_file_with_smbclient,
    list_shared_folder_with_smbclient,
    delete_file_with_smbclient,
    MachineInfo,
)
from server.config import MYSQL_CONFIG
import pytest


def test_get_machines():
    machines = get_machines(MYSQL_CONFIG)
    assert len(machines) > 0


def test_update_machine():
    machine_info = MachineInfo(*get_machines(MYSQL_CONFIG)[0])
    update_machine(MYSQL_CONFIG, machine_info)


@pytest.mark.skip(reason="skip smbclient test")
def test_send_file_with_smbclient():
    machine_info = get_machines(MYSQL_CONFIG)[0]
    send_file_with_smbclient(machine_info, "servers/main.py")


@pytest.mark.skip(reason="skip smbclient test")
def test_list_shared_folder_with_smbclient():
    machine_info = get_machines(MYSQL_CONFIG)[0]
    files = list_shared_folder_with_smbclient(machine_info)
    print(files)


@pytest.mark.skip(reason="skip smbclient test")
def test_delete_file_with_smbclient():
    machine_info = get_machines(MYSQL_CONFIG)[0]
    delete_file_with_smbclient(machine_info, "servers/main.py")
