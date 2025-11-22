"""
Cliente MongoDB (motor async).

Funções principais:
- Ler variáveis de ambiente
- Criar um cliente MongoDB assíncrono (singleton)
- Disponibilizar get_db() para outros módulos usarem
com o banco de dados configurado.
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient


# ________________________________________________________________________________________
# Configurações via variáveis de ambiente
# ________________________________________________________________________________________
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
MONGO_DB = os.getenv("MONGO_DB", "transflow")


# ________________________________________________________________________________________
# Cliente MongoDB Singleton
# ________________________________________________________________________________________
# A variável _client começa vazia e só é criada na primeira chamada de get_client().
_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    """
    Retorna uma instância única (singleton) do AsyncIOMotorClient.

    Caso ainda não exista, cria usando MONGO_URI.
    """
    global _client

    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URI)

    return _client


# ________________________________________________________________________________________
# Função para retornar o banco
# ________________________________________________________________________________________
def get_db():
    """
    Retorna a instância do banco MongoDB configurado em MONGO_DB.

    Use esta função para realizar operações assíncronas com o Motor.
    """
    return get_client()[MONGO_DB]
