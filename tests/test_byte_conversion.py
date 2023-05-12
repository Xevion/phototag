from phototag.helpers import convert_to_bytes


def test_basic():
    assert convert_to_bytes("1 Kb") == 128
    assert convert_to_bytes("1Mb") == 1024 ** 2 / 8
    assert convert_to_bytes("1 KB") == 1024
    assert convert_to_bytes("1 MB") == 1024 ** 2
    assert convert_to_bytes("1 KiB") == 1024
    assert convert_to_bytes("1TiB") == 1024 ** 4
    assert convert_to_bytes("1Tib") == 1024 ** 4 / 8
    assert convert_to_bytes("1tib") == 1000 ** 4 / 8
