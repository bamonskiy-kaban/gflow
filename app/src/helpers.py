from opensearchpy import AsyncOpenSearch
from dissect.target.target import Target

from config import OPENSEARCH_HOST, OPENSEARCH_PORT
from dataclasses import dataclass
from typing import Optional

import json

INDEX_CONFIG_PATH = 'index_config/index_config.json'


async def create_index(index_name: str):
    with open(INDEX_CONFIG_PATH) as file:
        cfg = json.load(file)

    async with AsyncOpenSearch(hosts=[{"host": OPENSEARCH_HOST, "port": int(OPENSEARCH_PORT)}],
                               use_ssl=False) as client:
        if await client.indices.exists(index=index_name):
            raise ValueError(f"Index [{index_name}] has already exist")

        await client.indices.create(
            index=index_name,
            body=cfg
        )


@dataclass
class TargetInfo:
    os: str
    hostname: str
    domain: Optional[str]
    version: str
    ips: str


def get_target_info(target_path: str) -> TargetInfo:
    target = Target.open(target_path)

    if not hasattr(target, "os"):
        raise Exception(f"No OS plugin found for target: {target_path}")

    if not hasattr(target, "hostname"):
        raise Exception(f"No hostname found for target: {target_path}")

    hostname = getattr(target, "hostname")
    domain = getattr(target, "domain") if hasattr(target, "domain") else None

    os = getattr(target, "os")
    version = getattr(target, "version") if hasattr(target, "version") else None
    ips_list = getattr(target, "ips") if hasattr(target, "ips") else []
    ips = ",".join(ips_list)

    return TargetInfo(
        os=os,
        hostname=hostname,
        domain=domain,
        version=version,
        ips=ips
    )
