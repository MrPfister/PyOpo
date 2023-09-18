import json
import struct
from functools import lru_cache
from pyopo.filehandler_filesystem import *
from typing import Self

from dataclasses import dataclass

import logging
import logging.config

logging.config.fileConfig(fname="logger.conf")
_logger = logging.getLogger()
# _logger.setLevel(logging.DEBUG)


@dataclass
class dbf_record:
    record_type: int

    @classmethod
    def from_bytes(self, record_header: bytes) -> Self:
        raise NotImplementedError()
        return dbf_record()

    def to_bytes(self) -> bytes:
        raise NotImplementedError()


@dataclass
class dbf_header:
    filetype: str
    dbf_version: int
    header_size: int
    minimum_supported_version: int
    extended_header: bytes

    @staticmethod
    @lru_cache
    def magic_word() -> str:
        return "OPLDatabaseFile"

    @classmethod
    @lru_cache
    def default() -> Self:
        return dbf_header(
            filetype=dbf_header.magic_word(),
            dbf_version=0,
            header_size=22,
            minimum_supported_version=0,
            extended_header=bytes(),
        )

    @classmethod
    def from_bytes(header_bytes: bytes) -> Self:
        # Minimum dbf.fmt header length
        assert len(header_bytes) >= 22

        header = dbf_header()

        header.filetype = header_bytes[0:15].decode()
        if header.filetype != dbf_header.magic_word():
            raise ImportError("Not a valid OPL Database File")

        (
            header.dbf_version,
            header.header_size,
            header.minimum_supported_version,
        ) = struct.unpack_from("<HHH", header_bytes, 16)

        # Accessible via DbfExtHeaderRead Sys Call only
        header.extended_header = header_bytes[22 : header["header_size"] - 22]

        return header

    def to_bytes(self) -> bytes:
        return struct.pack(
            "<15sHHH",
            self.filetype,
            self.dbf_version,
            self.header_size,
            self.minimum_supported_version,
        )


class dbf:
    def __init__(self, executable, filename) -> None:
        self.executable = executable
        self.filename: str = filename
        self.translated_Filename: str = translate_path_from_sibo(
            self.filename, self.executable
        )
        self.binary = None

        self.header: dbf_header = None

        self.records = []

        # This acts as a template which the current record clones from.
        self.header_fields = {}

        self.current_record = {}
        self.current_record_index = 0

    def load(self) -> None:
        _logger.debug(f" - Loading DBF File: {self.translated_Filename}")
        with open(self.translated_Filename, "rb") as file:
            self.binary = file.read()

        self.header = dbf_header.from_bytes(self.binary)
        self.records = self.read_records()

        _logger.debug(json.dumps(self.header, indent=2))
        _logger.debug(json.dumps(self.records, indent=2))

        input()

    def create(self) -> None:
        self.header = dbf_header.default()
        self.records = []

    def append(self) -> None:
        self.records.append(self.current_record.copy())
        self.current_record = self.header_fields.copy()

    def update(self):
        pass

    def create_record_header(self, records):
        # Write out Field record (type 2)

        record_types = []
        self.header_fields = {}
        for record in records:
            record_types.append(record[0])

            if record[0] == 0 or record[0] == 1:
                # Int16 Int32
                self.header_fields[record[1]] = 0
            elif record[0] == 2:
                # Float
                self.header_fields[record[1]] = 0.0
            else:
                # String
                self.header_fields[record[1]] = ""

        data_portion_size = len(record_types)
        data_record_type = 2  # Field information

        data_portion_size_binary = format(data_portion_size, "016b")
        data_record_type_binary = format(data_record_type, "08b")

        _logger.debug(data_portion_size_binary)
        _logger.debug(data_record_type_binary)

        header = data_record_type_binary[-4:] + data_portion_size_binary[-12:]
        _logger.debug(header)

        header_bytes = self.bitstring_to_bytes(header)

        record = {
            "record_header_bytes": [],
            "data_size": data_portion_size,
            "data_record_type": data_record_type,
            "record_data_bytes": record_types,
        }

        self.records = [record]

        self.current_record = self.header_fields.copy()

    def write_records(self):
        record_bytes = []

        for record in self.records:
            pass

    def read_records(self):
        self.records = []
        offset = self.header["header_size"]
        while True:
            record = {}

            record["record_header_bytes"] = struct.unpack_from(
                "<H", self.binary, offset
            )[0]

            header_bits = format(record["record_header_bytes"], "016b")
            record["data_size"] = int("0000" + header_bits[4:15], 2)
            record["data_record_type"] = int("0000" + header_bits[0:3], 2)

            _logger.debug(f"Data Size: {record['data_size']}")
            _logger.debug(f"Data Type: {record['data_record_type']}")

            record["record_data_bytes"] = self.binary[offset + 2 : record["data_size"]]

            self.records.append(self.unpack_record(record))

    def unpack_record(self, record):
        unpacked_record = record

        if record["data_record_type"] == 2:
            # Field Information Record

            for b in len(record["record_data_bytes"]):
                _logger.debug(record["record_data_bytes"][b])
                pass

            pass

        return unpacked_record

    def bitstring_to_bytes(self, s: str) -> bytes:
        return int(s, 2).to_bytes((len(s) + 7) // 8, byteorder="little")
