from broker import broker

from dissect.target.target import Target
from flow.record import iter_timestamped_records

from helpers import EventPacker
from event_writer import AsyncTcpEventWriter

from typing import Dict
from pathlib import Path

import logging

logger = logging.getLogger(__name__)

TARGET_ROOT = "/targets"


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
    record_packer = EventPacker(evidence_uid)

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
