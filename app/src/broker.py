from config import AMQP_URL, POSTGRES_URL
from taskiq_aio_pika import AioPikaBroker
from taskiq_pg.asyncpg import AsyncpgResultBackend


broker = AioPikaBroker(url=AMQP_URL).with_result_backend(AsyncpgResultBackend(dsn=POSTGRES_URL))