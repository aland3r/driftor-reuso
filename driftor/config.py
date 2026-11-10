"""PADRÃO SINGLETON, exemplo 1: Configuracao.

Lê as variáveis de ambiente uma única vez. Qualquer parte do código que fizer
Configuracao() recebe o MESMO objeto, então todo mundo enxerga a mesma edição
do produto e o mesmo endereço do banco.
"""

from __future__ import annotations

import os

# VARIABILIDADE: cada edição do produto liga um conjunto de recursos.
EDICOES = {
    "essencial": {"processos", "atividades"},
    "completa": {"processos", "atividades", "analises", "notas"},
}


class Configuracao:
    _instancia: Configuracao | None = None

    def __new__(cls) -> Configuracao:
        # Só cria o objeto na primeira chamada; nas outras devolve o mesmo.
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._carregar()
        return cls._instancia

    def _carregar(self) -> None:
        self.url_do_banco = os.environ.get(
            "DATABASE_URL", "postgresql://driftor_reuso:local@localhost:5432/driftor"
        )
        self.edicao = os.environ.get("EDICAO", "completa").lower()
        if self.edicao not in EDICOES:
            raise ValueError(f"EDICAO desconhecida: {self.edicao}. Use 'essencial' ou 'completa'.")

    def tem_recurso(self, recurso: str) -> bool:
        """Pergunta da variabilidade: esta edição tem o recurso?"""
        return recurso in EDICOES[self.edicao]

    def nome_da_edicao(self) -> str:
        return self.edicao.capitalize()
