"""PADRÃO ADAPTER, exemplo 1: o PM4Py adaptado à interface MineradorDeGrafo.

O app só conhece a interface MineradorDeGrafo (descobrir_arestas recebe Traces e
devolve Arestas). O PM4Py fala outra língua: quer uma tabela do pandas e devolve
um dicionário {(origem, destino): frequência}. O adaptador traduz de um para o outro.
Trocar o PM4Py por outra biblioteca exige mudar só esta classe.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

from driftor.dominio import Aresta, Trace


class MineradorDeGrafo(ABC):
    """Interface que o app espera (o "alvo" do Adapter)."""

    @abstractmethod
    def descobrir_arestas(self, traces: list[Trace]) -> list[Aresta]: ...


class Pm4pyMineradorAdapter(MineradorDeGrafo):
    """Adaptador: implementa a interface do app usando o PM4Py por dentro."""

    def descobrir_arestas(self, traces: list[Trace]) -> list[Aresta]:
        import pm4py  # biblioteca adaptada (o "adaptado")

        # 1. Traduz Traces do domínio para a tabela que o PM4Py entende.
        linhas = [
            {
                "case_id": trace.case_id,
                "atividade": evento.nome_no_grafo(),
                "momento": pd.Timestamp("2000-01-01", tz="UTC") + pd.Timedelta(seconds=posicao),
            }
            for trace in traces
            for posicao, evento in enumerate(trace.eventos)
        ]
        if not linhas:
            return []
        # 2. Chama o PM4Py: grafo de sequência direta (DFG).
        dfg, _inicios, _fins = pm4py.discover_dfg(
            pd.DataFrame(linhas), case_id_key="case_id", activity_key="atividade", timestamp_key="momento"
        )
        # 3. Traduz a resposta do PM4Py de volta para Arestas do domínio.
        return [Aresta(origem=o, destino=d, frequencia=int(n)) for (o, d), n in dfg.items()]
