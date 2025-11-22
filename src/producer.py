# Publica eventos no broker
# ...existing code...
"""
Producer que publica eventos 'corrida_finalizada' no RabbitMQ via aio_pika.
-----------------
Funções:
- publish_corrida(event): coroutine que publica o evento (json)
- publish_corrida_sync(event): helper síncrono para usar fora de loop async
-----------------
Obs: usa fila nomeada 'corrida_finalizada' e exchange default.
"""
import os
import json
import asyncio
from aio_pika import connect_robust, Message

#____________________________________________________________________________________________________________________
# Configuração do RabbitMQ
#____________________________________________________________________________________________________________________
RABBIT_URL = os.getenv("RABBIT_URL", "amqp://guest:guest@rabbitmq/")

#____________________________________________________________________________________________________________________
# Publicador assíncrono
#____________________________________________________________________________________________________________________
async def publish_corrida(event: dict):
    """
    Publica evento (dict) na fila 'corrida_finalizada'.
    """
    conn = await connect_robust(RABBIT_URL)

    async with conn:
        channel = await conn.channel()

        queue = await channel.declare_queue("corrida_finalizada", durable=True)

        body = json.dumps(event).encode()

        message = Message(body, content_type="application/json")

        await channel.default_exchange.publish(message, routing_key=queue.name)

#____________________________________________________________________________________________________________________
# Helper síncrono
#____________________________________________________________________________________________________________________
def publish_corrida_sync(event: dict):
    """
    Helper para publicar a partir de código síncrono (usa loop atual).
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        asyncio.create_task(publish_corrida(event))
    else:
        asyncio.run(publish_corrida(event))
