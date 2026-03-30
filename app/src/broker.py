from config import AMQP_URL, TASKIQ_BACKEND_POSTGRES_URL
from taskiq_aio_pika import AioPikaBroker
from taskiq_pg.psycopg import PsycopgResultBackend


broker = AioPikaBroker(url=AMQP_URL).with_result_backend(PsycopgResultBackend(dsn=TASKIQ_BACKEND_POSTGRES_URL))