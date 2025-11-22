"""
Consumer robusto para processar eventos 'corrida_finalizada'.

Fluxo:
1. Recebe mensagem do RabbitMQ
2. Faz parse e valida payload
3. Incrementa saldo do motorista no Redis
4. Salva/atualiza a corrida no MongoDB
5. Reconnect automático com backoff exponencial se cair
"""

import os
import asyncio
import json
import logging
from aio_pika import connect_robust, IncomingMessage, exceptions as aio_ex

from src.database.redis_cliente import incrementar_saldo
from src.database.mongo_client import get_db


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("consumer")

RABBIT_URL = os.getenv("RABBIT_URL", "amqp://guest:guest@rabbitmq:5672/")


# ________________________________________________________________________________________
# Função para tratar uma única mensagem recebida
# ________________________________________________________________________________________
async def handle_message(message: IncomingMessage):
    async with message.process():
        # --------------------------------------------------------------
        # Parse do JSON recebido
        # --------------------------------------------------------------
        try:
            payload = json.loads(message.body.decode())
        except Exception as e:
            logger.exception("Invalid message body: %s", e)
            return

        # --------------------------------------------------------------
        # Extração dos campos usados
        # --------------------------------------------------------------
        motorista = payload.get("motorista", {}).get("nome")

        try:
            valor = float(payload.get("valor_corrida", 0))
        except Exception:
            valor = 0.0

        # --------------------------------------------------------------
        # Incremento de saldo no Redis
        # --------------------------------------------------------------
        if motorista:
            try:
                await incrementar_saldo(motorista.lower(), valor)
                logger.info("Saldo incrementado para %s: +%s", motorista, valor)
            except Exception:
                logger.exception("Erro ao incrementar saldo para %s", motorista)

        # --------------------------------------------------------------
        # Upsert da corrida no MongoDB
        # --------------------------------------------------------------
        try:
            db = get_db()
            await db["corridas"].update_one(
                {"id_corrida": payload.get("id_corrida")},
                {"$set": payload},
                upsert=True
            )
            logger.info("Corrida upsert id=%s", payload.get("id_corrida"))
        except Exception:
            logger.exception("Erro ao salvar corrida no MongoDB")


# ________________________________________________________________________________________
# Loop principal de consumo com reconexão e backoff exponencial
# ________________________________________________________________________________________
async def consume_loop():
    backoff = 1

    while True:
        try:
            logger.info("Conectando ao RabbitMQ: %s", RABBIT_URL)
            conn = await connect_robust(RABBIT_URL)

            async with conn:
                channel = await conn.channel()
                await channel.set_qos(prefetch_count=10)

                queue = await channel.declare_queue(
                    "corrida_finalizada",
                    durable=True
                )

                logger.info("Consumindo fila 'corrida_finalizada'")

                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        await handle_message(message)

            backoff = 1  # Reset do backoff após sucesso

        except (aio_ex.AMQPConnectionError, ConnectionRefusedError) as e:
            logger.warning(
                "Erro conexão RabbitMQ: %s — reconectando em %s s",
                e, backoff
            )

        except Exception as e:
            logger.exception("Erro inesperado no consumer: %s", e)

        await asyncio.sleep(backoff)
        backoff = min(backoff * 2, 30)  # backoff máximo 30s


# ________________________________________________________________________________________
# Execução direta do script
# ________________________________________________________________________________________
if __name__ == "__main__":
    try:
        asyncio.run(consume_loop())
    except KeyboardInterrupt:
        logger.info("Consumer interrompido pelo usuário")
    except Exception:
        logger.exception("Consumer finalizou com erro")


