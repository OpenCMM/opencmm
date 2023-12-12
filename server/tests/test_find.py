from server import find
import csv


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
