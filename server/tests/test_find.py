from server import find
import csv

MYSQL_URL = "192.168.122.76"
# MYSQL_URL = "192.168.0.19"
MYSQL_PORT = "3306"

MYSQL_CONFIG = dict(
    host=MYSQL_URL,
    port=MYSQL_PORT,
    user="root",
    password="root",
)


def test_check_if_edge_is_found():
    assert find.check_if_edge_is_found("", "") is False
    assert find.check_if_edge_is_found("", 100.0) is True
    assert find.check_if_edge_is_found(100.0, "") is True
    assert find.check_if_edge_is_found(100.0, 99.9) is False
    assert find.check_if_edge_is_found(100.0, 50.0) is True
    assert find.check_if_edge_is_found(50.0, 100.0) is True
    assert find.check_if_edge_is_found(99.9, 100.0) is False
    assert find.check_if_edge_is_found(99.0, 100.0, 0.1) is True


def save_csv(filename, data):
    with open(filename, "w") as f:
        writer = csv.writer(f)
        writer.writerows(data)


def read_csv(filename):
    with open(filename, "r") as f:
        reader = csv.reader(f)
        data = []
        for row in reader:
            new_row = []
            for value in row:
                try:
                    new_row.append(float(value))
                except ValueError:
                    new_row.append(value)
            data.append(new_row)
        return data


def test_identify_close_edge_process_2():
    # process_id = 2
    # model_id = 2
    # measured_edges = find.find_edges(process_id, MYSQL_CONFIG)
    # save_csv(f"tests/fixtures/csv/process_{process_id}/measured_edges.csv", sensor_data)
    # edge_data = find.get_edge_data(model_id, MYSQL_CONFIG)
    # save_csv(f"tests/fixtures/csv/process_{process_id}/measured_edges.csv", sensor_data)

    measured_edges = read_csv("tests/fixtures/csv/process_2/measured_edges.csv")
    edge_data = read_csv("tests/fixtures/csv/process_2/edge_data.csv")
    _offset = (50.0, -65.0, 0.0)
    update_list = find.identify_close_edge(edge_data, measured_edges, _offset)
    edge_count = len(update_list)
    print(edge_count)
    assert edge_count > 0


def test_identify_close_edge_process_3():
    process_id = 3
    # model_id = 3
    # sensor_data = find.get_sensor_data(process_id, MYSQL_CONFIG)
    # save_csv(f"tests/fixtures/csv/process_{process_id}/measured_edges.csv", sensor_data)

    # measured_edges = find.find_edges(process_id, MYSQL_CONFIG)
    # save_csv(f"tests/fixtures/csv/process_{process_id}/measured_edges.csv", measured_edges)
    # edge_data = find.get_edge_data(model_id, MYSQL_CONFIG)
    # save_csv(f"tests/fixtures/csv/process_{process_id}/edge_data.csv", edge_data)

    measured_edges = read_csv(
        f"tests/fixtures/csv/process_{process_id}/measured_edges.csv"
    )
    edge_data = read_csv(f"tests/fixtures/csv/process_{process_id}/edge_data.csv")
    _offset = (0.0, 0.0, 0.0)
    update_list = find.identify_close_edge(edge_data, measured_edges, _offset)
    edge_count = len(update_list)
    print(edge_count)
    assert edge_count > 0


def test_identify_close_edge_process_4():
    process_id = 4
    # model_id = 3
    # measured_edges = find.find_edges(process_id, MYSQL_CONFIG)
    # save_csv(
    #     f"tests/fixtures/csv/process_{process_id}/measured_edges.csv", measured_edges
    # )
    # edge_data = find.get_edge_data(model_id, MYSQL_CONFIG)
    # save_csv(f"tests/fixtures/csv/process_{process_id}/edge_data.csv", edge_data)

    measured_edges = read_csv(
        f"tests/fixtures/csv/process_{process_id}/measured_edges.csv"
    )
    edge_data = read_csv(f"tests/fixtures/csv/process_{process_id}/edge_data.csv")
    _offset = (0.0, 0.0, 0.0)
    update_list = find.identify_close_edge(edge_data, measured_edges, _offset)
    edge_count = len(update_list)
    print(edge_count)
    assert edge_count > 0


def test_identify_close_edge_process_5():
    # process_id = 5
    # model_id = 2
    # measured_edges = find.find_edges(process_id, MYSQL_CONFIG)
    # save_csv(f"tests/fixtures/csv/process_{process_id}/measured_edges.csv", sensor_data)
    # edge_data = find.get_edge_data(model_id, MYSQL_CONFIG)
    # save_csv(f"tests/fixtures/csv/process_{process_id}/measured_edges.csv", sensor_data)

    measured_edges = read_csv("tests/fixtures/csv/process_5/measured_edges.csv")
    edge_data = read_csv("tests/fixtures/csv/process_5/edge_data.csv")
    _offset = (50.0, -65.0, 0.0)
    update_list = find.identify_close_edge(edge_data, measured_edges, _offset)
    edge_count = len(update_list)
    print(edge_count)
    assert edge_count > 0
