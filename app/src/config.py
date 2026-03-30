import os

AMQP_URL = os.getenv("AMQP_URL")
TASKIQ_BACKEND_POSTGRES_URL = os.getenv("BACKEND_POSTGRES_URL")
API_DB_POSTGRES_URL = os.getenv("API_DB_POSTGRES_URL")
OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST")
OPENSEARCH_PORT = int(os.getenv("OPENSEARCH_PORT", 0))
EVENT_BROKER_HOST = os.getenv("EVENT_BROKER_HOST")
EVENT_BROKER_PORT = int(os.getenv("EVENT_BROKER_PORT", 0))
DASHBOARDS_URL = ""
API_TARGETS_DIR = "/targets"
FUNCTIONS = {
    "windows": ["amcache", "services", "regf", "ual", "browser", "lnk"],
    "linux": []
}