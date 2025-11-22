"""
Modelos Pydantic usados para representar corridas.

Cada classe define como os dados devem aparecer:
- Passageiro: informações do passageiro
- Motorista: informações do motorista
- Corrida: documento principal que reúne tudo

Validações:
- valor_corrida não pode ser negativo

Métodos:
- to_mongo(): retorna o modelo em formato pronto para o MongoDB
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any

# ________________________________________________________________________________________
# Passageiro
# ________________________________________________________________________________________
class Passageiro(BaseModel):
    """
    Representa os dados básicos de um passageiro.
    """
    nome: str = Field(..., example="João")
    telefone: str = Field(..., example="99999-1111")


# ________________________________________________________________________________________
# Motorista
# ________________________________________________________________________________________
class Motorista(BaseModel):
    """
    Representa os dados básicos de um motorista.
    """
    nome: str = Field(..., example="Carla")
    nota: Optional[float] = Field(
        None,
        example=4.8,
        description="Avaliação do motorista (opcional)."
    )


# ________________________________________________________________________________________
# Corrida (Documento Principal)
# ________________________________________________________________________________________
class Corrida(BaseModel):
    """
    Representa uma corrida completa, incluindo:
    - passageiro
    - motorista
    - origem e destino
    - valor da corrida
    - forma de pagamento
    """
    id_corrida: str = Field(..., example="abc123")
    passageiro: Passageiro
    motorista: Motorista
    origem: str = Field(..., example="Centro")
    destino: str = Field(..., example="Inoã")
    valor_corrida: float = Field(..., example=35.5)
    forma_pagamento: str = Field(..., example="DigitalCoin")

    # ____________________________________________________________________________________
    # Validação: garantir valor_corrida >= 0
    # ____________________________________________________________________________________
    @validator("valor_corrida")
    def validar_valor_nao_negativo(cls, valor: float) -> float:
        """
        Garante que o valor da corrida não seja negativo.
        """
        if valor < 0:
            raise ValueError("valor_corrida deve ser não negativo")
        return valor

    # ____________________________________________________________________________________
    # Converter para MongoDB
    # ____________________________________________________________________________________
    def to_mongo(self) -> Dict[str, Any]:
        """
        Converte o modelo para um dicionário pronto para salvar no MongoDB.
        """
        return self.dict()
