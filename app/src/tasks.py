from broker import broker

from dissect.target.target import Target
from flow.record import iter_timestamped_records, Record, RecordDescriptor, fieldtypes

from event_writer import AsyncTcpEventWriter
from typing import Any
from datetime import datetime

from typing import Dict
from pathlib import Path

import orjson
import base64
import logging

logger = logging.getLogger(__name__)

TARGET_ROOT = "/targets"


class EvidenceJsonRecordPacker:
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


@broker.task
async def process_function(evidence_uid: str,
                           relative_path: str,
                           function_name: str,
                           tcp_event_broker_host: str,
                           tcp_event_broker_port: int) -> Dict:
    result_dict = {
        "evidence_uid": evidence_uid,
        "evidence_path": relative_path,
        "function_name": function_name,
        "records": 0,
        "error": None
    }

    try:
        target_path = Path(TARGET_ROOT) / relative_path
        target = Target.open(target_path)
    except Exception as e:
        logger.critical(f"Target initialization error: [{e}]", exc_info=True)
        result_dict["error"] = str(e)
        return result_dict

    if not target.has_function(function_name):
        result_dict["error"] = "No such function"
        logger.critical(
            f"No such function [{function_name}] for target - Evidence UID: [{evidence_uid}] | Target path: [{target_path}]")
        return result_dict

    _, function = target.get_function(function_name)

    count = 0
    record_packer = EvidenceJsonRecordPacker(evidence_uid)

    try:
        async with AsyncTcpEventWriter(tcp_event_broker_host, tcp_event_broker_port) as event_writer:
            for rec in function():
                for record in iter_timestamped_records(rec):
                    event = record_packer.pack(record)
                    await event_writer.write_event(event)
                    count += 1

    except Exception as e:
        logger.critical(f"Processing critical error: [{e}]", exc_info=True)
        result_dict["error"] = str(e)

    finally:
        logger.info(
            f"Processing completed. Target info - Evidence UID: [{evidence_uid}] | Target path: [{target_path}] | Function: [{function_name}]")
        result_dict["records"] = count
        return result_dict
