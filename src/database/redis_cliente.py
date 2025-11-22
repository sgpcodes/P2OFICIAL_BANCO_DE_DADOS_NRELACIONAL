"""
Cliente Redis assíncrono.

Responsabilidades:
- Criar um cliente Redis async (singleton)
- Ler saldo de um motorista
- Incrementar saldo com operação atômica (INCRBYFLOAT)

Chave utilizada no Redis:
saldo:{motorista}
"""

import os
from typing import Optional
import redis.asyncio as aioredis


# ________________________________________________________________________________________
# Configuração do Redis via variável de ambiente
# ________________________________________________________________________________________
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")


# ________________________________________________________________________________________
# Cliente Redis Singleton
# ________________________________________________________________________________________
# Começa vazio e é criado na primeira chamada de get_redis().
_redis_client: Optional[aioredis.Redis] = None


def get_redis() -> aioredis.Redis:
    """
    Retorna o cliente Redis assíncrono (singleton).

    decode_responses=True → Redis retorna strings legíveis
    em vez de bytes.
    """
    global _redis_client

    if _redis_client is None:
        _redis_client = aioredis.from_url(
            REDIS_URL,
            decode_responses=True
        )

    return _redis_client


# ________________________________________________________________________________________
# Ler saldo do motorista
# ________________________________________________________________________________________
async def get_saldo(motorista: str) -> float:
    """
    Retorna o saldo atual de um motorista.

    Caso a chave não exista no Redis → retorna 0.0
    """
    redis_client = get_redis()
    valor = await redis_client.get(f"saldo:{motorista}")

    return float(valor) if valor is not None else 0.0


# ________________________________________________________________________________________
# Incremento de saldo (operação atômica)
# ________________________________________________________________________________________
async def incrementar_saldo(motorista: str, valor: float) -> float:
    """
    Incrementa o saldo do motorista usando INCRBYFLOAT (atômico).
    Retorna o novo saldo atualizado.
    """
    redis_client = get_redis()
    return await redis_client.incrbyfloat(f"saldo:{motorista}", valor)


