"""Tests for scripts/archaeology/formats.py on inline synthetic sources (no legacy data)."""

from __future__ import annotations

from scripts.archaeology import formats as f

PATH = "sportorg/modules/sportident/reader.py"


def _values(rows: list[f.FunctionRow], kind: str) -> list[f.Value]:
    return [v for row in rows for v in row.values if v.kind == kind]


def test_extracts_baudrate_and_timeout_literals() -> None:
    src = (
        "import serial\n"
        "def connect(port):\n"
        "    return serial.Serial(port, baudrate=38400, timeout=5)\n"
    )
    rows = f.scan_source(src, PATH)
    assert [r.function for r in rows] == ["connect"]
    assert rows[0].direction == "device"
    assert rows[0].kinds == ("serial",)
    assert rows[0].calls[0].line == 3
    baud = _values(rows, "baudrate")
    timeout = _values(rows, "timeout")
    assert [(v.text, v.line) for v in baud] == [("38400", 3)]
    assert [(v.text, v.line) for v in timeout] == [("5", 3)]


def test_positional_serial_arguments() -> None:
    src = "import serial\ndef connect():\n    return serial.Serial('COM3', 4800)\n"
    rows = f.scan_source(src, PATH)
    assert [v.text for v in _values(rows, "port")] == ["'COM3'"]
    assert [v.text for v in _values(rows, "baudrate")] == ["4800"]


def test_extracts_open_encoding() -> None:
    src = (
        "def save(name, text):\n"
        "    with open(name + '.csv', 'w', encoding='cp1251', newline='') as fh:\n"
        "        fh.write(text)\n"
        "def load(name):\n"
        "    with open(name, encoding='utf-8') as fh:\n"
        "        return fh.read()\n"
    )
    rows = {r.function: r for r in f.scan_source(src, PATH)}
    assert rows["save"].direction == "write"
    assert rows["load"].direction == "read"
    assert [v.text for v in _values([rows["save"]], "encoding")] == ["'cp1251'"]
    assert [v.text for v in _values([rows["load"]], "encoding")] == ["'utf-8'"]
    assert [v.text for v in _values([rows["save"]], "extension")] == ["'.csv'"]
    assert [v.text for v in _values([rows["save"]], "delimiter")] == ["''"]


def test_open_mode_direction() -> None:
    src = (
        "def a(p):\n    open(p, 'r+b')\n"
        "def b(p, m):\n    open(p, m)\n"
        "def c(p):\n    open(p, mode='ab')\n"
    )
    rows = {r.function: r for r in f.scan_source(src, PATH)}
    assert rows["a"].direction == "both"
    assert rows["a"].kinds == ("binary file",)
    assert rows["b"].direction == "unknown"
    assert rows["c"].direction == "write"


def test_struct_format_and_byte_constants() -> None:
    src = (
        "import struct\n"
        "def parse(data):\n"
        "    if data[0] == 0x02 and data[5:9] == b'\\xff\\x03':\n"
        "        return struct.unpack('>HBI', data[1:8])\n"
        "    return None\n"
    )
    rows = f.scan_source(src, PATH)
    assert rows[0].direction == "read"
    assert [v.text for v in _values(rows, "struct-format")] == ["'>HBI'"]
    consts = _values(rows, "byte-constant")
    assert {v.text for v in consts} == {"0x02", "b'\\xff\\x03'"}
    widths = {v.text for v in _values(rows, "offset-or-width")}
    assert {"5", "9", "8"} <= widths


def test_module_constant_resolved_to_assignment_line() -> None:
    src = (
        "import serial\n"
        "\n"
        "BAUD_RATE = 9600\n"
        "STX = b'\\x02'\n"
        "\n"
        "def open_port(name):\n"
        "    port = serial.Serial(name, baudrate=BAUD_RATE)\n"
        "    port.write(STX)\n"
        "    return port\n"
    )
    rows = f.scan_source(src, PATH)
    baud = _values(rows, "baudrate")
    assert [(v.text, v.line, v.use_line) for v in baud] == [("9600", 3, 7)]
    assert baud[0].origin == "constant BAUD_RATE via keyword baudrate of serial.Serial"
    stx = _values(rows, "byte-constant")
    assert [(v.text, v.line, v.use_line) for v in stx] == [("b'\\x02'", 4, 8)]


def test_class_constant_through_self() -> None:
    src = (
        "import serial\n"
        "class Reader:\n"
        "    TIMEOUT = 3\n"
        "    def connect(self):\n"
        "        return serial.Serial('COM1', timeout=self.TIMEOUT)\n"
    )
    rows = f.scan_source(src, PATH)
    assert rows[0].function == "Reader.connect"
    assert [(v.text, v.line, v.use_line) for v in _values(rows, "timeout")] == [("3", 3, 5)]


def test_formats_json_csv_xml_and_aliases() -> None:
    src = (
        "import json as js\n"
        "import xml.etree.ElementTree as ET\n"
        "from csv import DictWriter\n"
        "def a(s):\n    return js.loads(s)\n"
        "def b(p):\n    return ET.parse(p)\n"
        "def c(fh):\n    return DictWriter(fh, [], delimiter=';')\n"
    )
    rows = {r.function: r for r in f.scan_source(src, "sportorg/models/memory.py")}
    assert (rows["a"].kinds, rows["a"].direction) == (("JSON",), "read")
    assert (rows["b"].kinds, rows["b"].direction) == (("XML",), "read")
    assert (rows["c"].kinds, rows["c"].direction) == (("CSV",), "write")
    assert [v.text for v in _values([rows["c"]], "delimiter")] == ["';'"]
    assert rows["a"].context == "race file (JSON)"


def test_function_without_io_has_no_row() -> None:
    assert f.scan_source("def f():\n    return 1\n", PATH) == []


def test_url_and_email_redaction() -> None:
    src = (
        "import requests\n"
        "def push():\n"
        "    requests.post('https://example.invalid/api', timeout=3)\n"
        "    return 'a.b@example.com'\n"
    )
    rows = f.scan_source(src, PATH)
    assert rows[0].direction == "write"
    assert [v.text for v in _values(rows, "url")] == ["'https://example.invalid/api'"]
    assert f.redact("'a.b@example.com'") == "<redacted: e-mail>"


def test_summary_lists_formats_without_reader_or_writer() -> None:
    src = (
        "import json\nimport csv\n"
        "def a(s):\n    return json.loads(s)\n"
        "def b(fh):\n    return csv.writer(fh)\n"
    )
    rows = f.scan_source(src, PATH)
    summary = f.summarise(rows)
    assert summary["without_writer"] == ["JSON"]
    assert summary["without_reader"] == ["CSV"]
    assert summary["by_kind_direction"] == {"CSV": {"write": 1}, "JSON": {"read": 1}}


def test_struct_format_from_class_constant_and_xml_write() -> None:
    src = (
        "import struct\n"
        "from lxml import etree\n"
        "class Header:\n"
        "    fmt = '=2s2H'\n"
        "    def pack(self):\n"
        "        return struct.pack(self.fmt, b'SO', 1, 2)\n"
        "def export(tree, fh):\n"
        "    etree.ElementTree(tree).write(fh, encoding='utf-8')\n"
    )
    rows = {r.function: r for r in f.scan_source(src, PATH)}
    fmt = _values([rows["Header.pack"]], "struct-format")
    assert [(v.text, v.line, v.use_line) for v in fmt] == [("'=2s2H'", 4, 6)]
    assert (rows["export"].kinds, rows["export"].direction) == (("XML",), "write")


def test_serial_method_calls_count_as_device_io() -> None:
    src = (
        "def fetch(serial):\n"
        "    return serial.read(8)\n"
        "class Station:\n"
        "    def send(self):\n"
        "        self._serial.write(b'\\x01')\n"
    )
    rows = {r.function: r for r in f.scan_source(src, "sportorg/libs/sportiduino/x.py")}
    assert (rows["fetch"].kinds, rows["fetch"].direction) == (("Sportiduino serial",), "read")
    assert rows["fetch"].calls[0].line == 2
    assert rows["Station.send"].direction == "write"
    assert [v.text for v in _values([rows["Station.send"]], "byte-constant")] == ["b'\\x01'"]


def test_protocol_decoder_without_io_gets_row() -> None:
    src = (
        "STX = 0x02\n"
        "def parse(data):\n"
        "    if data[0] != b'\\xaa':\n"
        "        return None\n"
        "    return (data[3] << 8 | data[4]) & 0x0FFF\n"
    )
    rows = f.scan_source(src, PATH)
    assert [(r.function, r.direction) for r in rows] == [("parse", "decode")]
    assert rows[0].calls[0].api == "<protocol>"
    texts = {v.text for v in _values(rows, "byte-constant")}
    assert {"b'\\xaa'", "0x0FFF"} <= texts
    assert "8" in {v.text for v in _values(rows, "offset-or-width")}


def test_protocol_encoder_and_other_contexts() -> None:
    src = "def build(n):\n    return n.to_bytes(2, 'big')\n"
    rows = f.scan_source(src, PATH)
    assert [(r.function, r.direction) for r in rows] == [("build", "encode")]
    assert f.scan_source("def f(d):\n    return d[1] << 8\n", "sportorg/utils/x.py") == []


def test_vocabulary_miss_is_not_io() -> None:
    src = "def f(items):\n    return items.read()\n"
    assert f.scan_source(src, "sportorg/utils/x.py") == []
