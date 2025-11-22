# FastAPI principal (rotas e endpoints)
# ________________________________________________________________________________________

"""
FastAPI principal com endpoints mínimos exigidos pelo trabalho.

Endpoints:
- POST /corridas                     → cadastra nova corrida e publica evento
- GET /corridas                      → lista corridas (limite 1000)
- GET /corridas/{forma_pagamento}   → filtra por forma de pagamento
- GET /saldo/{motorista}            → retorna saldo atual do motorista (Redis)

Notas:
- O consumer é quem faz o processamento assíncrono:
    → atualiza saldo no Redis
    → confirma a corrida no MongoDB
- Esta API apenas insere/atualiza o documento inicial
  e envia o evento para a fila.
"""

import os
from typing import List

from fastapi import FastAPI
import uvicorn

from src.database.mongo_client import get_db
from src.database.redis_cliente import get_saldo
from src.models.corrida_model import Corrida
from src.producer import publish_corrida


# ________________________________________________________________________________________
# Instância principal do FastAPI
# ________________________________________________________________________________________
app = FastAPI(title="TransFlow - API")


# ________________________________________________________________________________________
# POST /corridas  → cria nova corrida e publica evento
# ________________________________________________________________________________________
@app.post("/corridas", status_code=201)
async def criar_corrida(corrida: Corrida):
    """
    Recebe uma corrida, armazena no Mongo (upsert)
    e publica evento 'corrida_finalizada'.

    O processamento real (saldo e storage final)
    é feito pelo consumer.
    """
    documento = corrida.to_mongo()
    db = get_db()

    # Upsert imediato no MongoDB
    await db["corridas"].update_one(
        {"id_corrida": documento["id_corrida"]},
        {"$set": documento},
        upsert=True
    )

    # Publicação do evento
    await publish_corrida(documento)

    return {"ok": True, "id_corrida": documento["id_corrida"]}


# ________________________________________________________________________________________
# GET /corridas  → lista até 1000 corridas
# ________________________________________________________________________________________
@app.get("/corridas", response_model=List[Corrida])
async def listar_corridas():
    """
    Lista até 1000 documentos da coleção 'corridas'.
    """
    db = get_db()
    return await db["corridas"].find().to_list(length=1000)


# ________________________________________________________________________________________
# GET /corridas/{forma_pagamento}  → filtra por tipo de pagamento
# ________________________________________________________________________________________
@app.get("/corridas/{forma_pagamento}", response_model=List[Corrida])
async def filtrar_corridas(forma_pagamento: str):
    """
    Retorna as corridas que possuem a forma de pagamento informada.
    """
    db = get_db()
    return await db["corridas"].find({
        "forma_pagamento": forma_pagamento
    }).to_list(length=1000)


# ________________________________________________________________________________________
# GET /saldo/{motorista}  → saldo atual do motorista
# ________________________________________________________________________________________
@app.get("/saldo/{motorista}")
async def ver_saldo(motorista: str):
    """
    Retorna o saldo atual do motorista (obtido diretamente do Redis).
    """
    saldo = await get_saldo(motorista.lower())
    return {"motorista": motorista, "saldo": saldo}


# ________________________________________________________________________________________
# Entrypoint (útil para desenvolvimento local)
# ________________________________________________________________________________________
if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=False
    )
