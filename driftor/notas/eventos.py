"""PADRÃO OBSERVER, exemplo 2: quando uma nota de drift é criada ou excluída.

Sujeito: publicador_de_notas. Observadores: ContadorDeNotas (abaixo) e
AvisoNaTela (driftor/observador.py). As inscrições ficam em driftor/main.py.
"""

from __future__ import annotations

from driftor.banco import BancoDeDados
from driftor.observador import Observador, Sujeito

publicador_de_notas = Sujeito()


class ContadorDeNotas(Observador):
    """Mantém em dia o total de notas que aparece no cartão da análise."""

    def atualizar(self, evento: str, dados: dict) -> None:
        if evento in ("nota_criada", "nota_excluida"):
            BancoDeDados().executar(
                """update analises set total_notas = (
                       select count(*) from notas_drift n join drifts d on d.id = n.drift_id
                       where d.analise_id = :analise_id)
                   where id = :analise_id""",
                analise_id=dados["analise_id"],
            )
