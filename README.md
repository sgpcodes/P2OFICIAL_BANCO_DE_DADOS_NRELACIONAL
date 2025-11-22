# ...existing code...
# TransFlow - protótipo

Instalação local (venv):
1. python -m venv .venv
2. .venv\Scripts\activate
3. pip install -r requirements.txt
4. export vars (ou use .env):
   - MONGO_URI (padrão: mongodb://mongo:27017)
   - REDIS_URL (padrão: redis://redis:6379/0)
   - RABBIT_URL (padrão: amqp://guest:guest@rabbitmq/)
5. Rodar consumer em background (opcional):
   python -m src.consumer
6. Rodar app:
   uvicorn src.main:app --host 0.0.0.0 --port 8000

Ou com Docker Compose:
  docker-compose up --build

Endpoints:
- POST /corridas  (body = Corrida)
- GET /corridas
- GET /corridas/{forma_pagamento}
- GET /saldo/{motorista}

# ...existing code...# TransFlow — Protótipo

TransFlow é um protótipo de sistema para processar corridas: API que registra corridas, publica eventos em RabbitMQ e um consumer que atualiza saldo no Redis e confirma o registro no MongoDB.

Principais componentes
- API (FastAPI) — endpoints para criar/listar corridas e consultar saldo. ([src/main.py](src/main.py))
- Producer — publica eventos `corrida_finalizada` no RabbitMQ. ([src/producer.py](src/producer.py))
- Consumer — consome a fila, incrementa saldo no Redis e upserta o documento no MongoDB. ([src/consumer.py](src/consumer.py))
- Clientes DB:
  - Mongo: [src/database/mongo_client.py](src/database/mongo_client.py)
  - Redis: [src/database/redis_cliente.py](src/database/redis_cliente.py)
- Modelos Pydantic: [src/models/corrida_model.py](src/models/corrida_model.py)
- Orquestração: [docker-compose.yml](docker-compose.yml)

Requisitos
- Docker + Docker Compose (recomendado)
- Python 3.11 (se rodar local sem Docker)
- virtualenv (opcional, para execução local)

Variáveis de ambiente (exemplo em `.env`)
- MONGO_URI (padrão: `mongodb://mongo:27017`)
- MONGO_DB (padrão no código: `transflow`; .env do projeto contém `p2_bd`)
- REDIS_URL (padrão: `redis://redis:6379/0`)
- RABBIT_URL (padrão: `amqp://guest:guest@rabbitmq:5672/`)
- HOST, PORT, LOG_LEVEL, etc.

Observação importante
- O cliente Mongo usa a variável `MONGO_DB`. No código o padrão é `transflow` (veja [src/database/mongo_client.py](src/database/mongo_client.py)), mas o arquivo `.env` do projeto define `MONGO_DB=p2_bd`. Ajuste conforme desejar para manter consistência.

Execução (Docker Compose)
1. Build + up:
   docker-compose up --build

2. Serviços expostos:
   - API: http://localhost:8000
   - RabbitMQ management: http://localhost:15672 (guest/guest)
   - Mongo: 27017
   - Redis: 6379

Execução local sem Docker (dev)
1. python -m venv .venv
2. .venv\Scripts\activate
3. pip install -r requirements.txt
4. Defina variáveis de ambiente (ou crie `.env`)
5. Rodar API:
   uvicorn src.main:app --host 0.0.0.0 --port 8000
6. Rodar consumer (opcional):
   python -m src.consumer

Endpoints principais
- POST /corridas
  - Body: modelo Corrida (veja [src/models/corrida_model.py](src/models/corrida_model.py))
  - Comportamento: faz upsert imediato no Mongo e publica evento `corrida_finalizada` no RabbitMQ.
- GET /corridas
  - Lista corridas (até 1000)
- GET /corridas/{forma_pagamento}
  - Filtra por forma de pagamento
- GET /saldo/{motorista}
  - Lê saldo do Redis (chave `saldo:{motorista}`)

Exemplos rápidos

PowerShell — criar corrida:
$body = @{
  id_corrida = "test_123"
  passageiro = @{ nome="Teste"; telefone="99999-0000" }
  motorista   = @{ nome="Carla"; nota = 4.9 }
  origem = "Centro"
  destino = "Praia"
  valor_corrida = 12.5
  forma_pagamento = "Cartao"
} | ConvertTo-Json -Depth 10 -Compress

Invoke-RestMethod -Uri http://localhost:8000/corridas -Method Post -Body $body -ContentType 'application/json; charset=utf-8'

curl — obter saldo:
curl -s http://localhost:8000/saldo/carla

Verificações úteis (via Docker)
- Ver documentos no Mongo:
  docker-compose exec -T mongo mongosh --quiet --eval "printjson(db.getSiblingDB('transflow').corridas.find().limit(5).toArray())"
  (substitua `transflow` por `p2_bd` se for o DB escolhido)

- Ver saldo no Redis:
  docker-compose exec redis redis-cli GET saldo:carla

- Ver filas RabbitMQ:
  docker-compose exec rabbitmq rabbitmqctl list_queues

Dicas de debug
- Logs do consumer mostram consumo e operações: `docker-compose logs -f consumer`
- Se consumer não conectar ao RabbitMQ, verifique health/status do rabbitmq e variáveis RABBIT_URL
- Consistência de nome do DB: alinhe `MONGO_DB` em `.env` com o valor usado em [src/database/mongo_client.py](src/database/mongo_client.py)

Arquivos importantes
- [src/main.py](src/main.py)
- [src/consumer.py](src/consumer.py)
- [src/producer.py](src/producer.py)
- [src/database/mongo_client.py](src/database/mongo_client.py)
- [src/database/redis_cliente.py](src/database/redis_cliente.py)
- [src/models/corrida_model.py](src/models/corrida_model.py)
- [docker-compose.yml](docker-compose.yml)
- [.env](.env)

Contribuição
- Abra uma issue com bugs ou melhorias.
- PRs bem-vindas: mantenha estilo simples e testes/descrição curta.

Licença
- Sem licença definida. Adicione uma license file se desejar (ex: MIT).
