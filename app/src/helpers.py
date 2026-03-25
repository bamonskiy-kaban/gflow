from opensearchpy import AsyncOpenSearch
from pygments.lexer import default

from config import OPENSEARCH_HOST, OPENSEARCH_PORT
from typing import Any
from datetime import datetime

from flow.record import Record, RecordDescriptor
from flow.record import fieldtypes

import json
import orjson
import base64


INDEX_CONFIG_PATH = 'index_config/index_config.json'


async def create_index(index_name: str):
    with open(INDEX_CONFIG_PATH) as file:
        cfg = json.load(file)

    async with AsyncOpenSearch(hosts=[{"host": OPENSEARCH_HOST, "port": int(OPENSEARCH_PORT)}], use_ssl=False) as client:
        if await client.indices.exists(index=index_name):
            raise ValueError(f"Index [{index_name}] has already exist")
        await client.indices.create(
            index=index_name,
            body=cfg
        )


# TODO: костыль, внедрить в dissect
class EventPacker:
    def __init__(self, evidence_uid: str):
        self.evidence_uid = evidence_uid

    def pack_obj(self, obj: Any):
        if isinstance(obj, Record):
            serial = obj._asdict()

            serial["_type"] = "record"
            serial["_recorddescriptor"] = obj._desc.identifier

            for field_type, field_name in obj._desc.get_field_tuples():
                # Boolean field types should be cast to a bool instead of staying ints
                if field_type == "boolean" and isinstance(serial[field_name], int):
                    serial[field_name] = bool(serial[field_name])

            serial["evidence_uid"] = self.evidence_uid

            return serial
        if isinstance(obj, RecordDescriptor):
            return {
                "_type": "recorddescriptor",
                "_data": obj._pack(),
            }
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, fieldtypes.digest):
            return {
                "md5": obj.md5,
                "sha1": obj.sha1,
                "sha256": obj.sha256,
            }
        if isinstance(obj, (fieldtypes.net.ipaddress, fieldtypes.net.ipnetwork, fieldtypes.net.ipinterface)):
            return str(obj)
        if isinstance(obj, bytes):
            return base64.b64encode(obj).decode()
        if isinstance(obj, fieldtypes.path):
            return str(obj)
        if isinstance(obj, fieldtypes.command):
            return {
                "executable": obj.executable,
                "args": obj.args,
            }

        raise TypeError(f"Unpackable type {type(obj)}")

    def pack(self, obj: Any):
        return orjson.dumps(obj, default=self.pack_obj)

