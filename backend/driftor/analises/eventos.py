"""PADRÃO OBSERVER, exemplo 1: quando uma análise termina, quem precisa saber é avisado.

Sujeito: publicador_de_analise. Observadores: AtualizadorDoProcesso (abaixo) e
AvisoNaTela (driftor/observador.py). As inscrições ficam em driftor/main.py.
"""

from __future__ import annotations

from driftor.banco import BancoDeDados
from driftor.observador import Observador, Sujeito

publicador_de_analise = Sujeito()


class AtualizadorDoProcesso(Observador):
    """Marca o processo como recém-movimentado, para ele subir na lista de processos."""

    def atualizar(self, evento: str, dados: dict) -> None:
        if evento == "analise_concluida":
            BancoDeDados().executar(
                "update processos set atualizado_em = now() where id = :id", id=dados["processo_id"]
            )
