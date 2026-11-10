"""Acesso ao banco do CRUD de Análise: tabelas analises e drifts."""

from __future__ import annotations

import json

from driftor.dominio import Analise, Drift
from driftor.repositorio_base import RepositorioBase


class RepositorioDeAnalises(RepositorioBase[Analise]):
    # obter, obter_ou_erro e excluir vêm de RepositorioBase
    tabela = "analises"
    colunas = "id, processo_id, nome, delta, tratamento, atividade, total_observacoes"
    nome_no_singular = "análise"

    def criar_objeto(self, linha: dict) -> Analise:
        """A análise vem com os seus desvios (tabela drifts)."""
        analise = Analise(**{**linha, "id": str(linha["id"]), "processo_id": str(linha["processo_id"])})
        analise.drifts = [
            Drift(**{**d, "id": str(d["id"])})
            for d in self.banco.consultar(
                """select id, posicao, indice, inicio_anomalia, media_antes, media_depois, variacao_pct
                   from drifts where analise_id = :id order by posicao""",
                id=analise.id,
            )
        ]
        return analise

    # ---- Read
    def listar_resumo(self, processo_id: str | None = None) -> list[dict]:
        filtro = "where a.processo_id = :processo_id" if processo_id else ""
        return self.banco.consultar(
            f"""select a.id, a.nome, a.atividade, a.delta, a.tratamento, a.total_observacoes,
                       a.total_drifts, a.total_notas, a.criado_em, p.nome as processo
                from analises a join processos p on p.id = a.processo_id
                {filtro} order by a.criado_em desc""",
            processo_id=processo_id,
        )

    def serie(self, id: str) -> list[float]:
        linha = self.banco.consultar_um("select serie from analises where id = :id", id=id)
        return json.loads(linha["serie"]) if linha else []

    # ---- Create
    def inserir(self, analise: Analise, serie: list[float]) -> None:
        self.banco.executar(
            """insert into analises (id, processo_id, nome, atividade, delta, tratamento,
                                     total_observacoes, total_drifts, serie)
               values (:id, :processo_id, :nome, :atividade, :delta, :tratamento,
                       :total_observacoes, :total_drifts, :serie)""",
            id=analise.id, processo_id=analise.processo_id, nome=analise.nome, atividade=analise.atividade,
            delta=analise.delta, tratamento=analise.tratamento, total_observacoes=analise.total_observacoes,
            total_drifts=len(analise.drifts), serie=json.dumps(serie),
        )
        self.banco.executar_varios(
            """insert into drifts (id, analise_id, posicao, indice, inicio_anomalia, media_antes, media_depois, variacao_pct)
               values (:id, :analise_id, :posicao, :indice, :inicio_anomalia, :media_antes, :media_depois, :variacao_pct)""",
            [{**vars(d), "analise_id": analise.id} for d in analise.drifts],
        )

    # ---- Update
    def renomear(self, analise: Analise) -> None:
        self.banco.executar("update analises set nome = :nome where id = :id", id=analise.id, nome=analise.nome)

    # ---- Delete: herdado; drifts e notas caem junto (on delete cascade)
