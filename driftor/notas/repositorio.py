"""Acesso ao banco do CRUD de Nota de drift: tabela notas_drift."""

from __future__ import annotations

from driftor.dominio import NotaDeDrift
from driftor.repositorio_base import RepositorioBase


class RepositorioDeNotas(RepositorioBase[NotaDeDrift]):
    # obter, obter_ou_erro e excluir vêm de RepositorioBase
    tabela = "notas_drift"
    colunas = "id, drift_id, texto"
    nome_no_singular = "nota"

    def criar_objeto(self, linha: dict) -> NotaDeDrift:
        return NotaDeDrift(str(linha["id"]), str(linha["drift_id"]), linha["texto"])

    # ---- Read
    def listar_da_analise(self, analise_id: str) -> list[dict]:
        return self.banco.consultar(
            """select n.id, n.drift_id, n.texto, n.atualizado_em, d.posicao
               from notas_drift n join drifts d on d.id = n.drift_id
               where d.analise_id = :analise_id order by d.posicao, n.criado_em""",
            analise_id=analise_id,
        )

    # ---- Create
    def inserir(self, nota: NotaDeDrift) -> None:
        self.banco.executar(
            "insert into notas_drift (id, drift_id, texto) values (:id, :drift_id, :texto)",
            id=nota.id, drift_id=nota.drift_id, texto=nota.texto,
        )

    # ---- Update
    def atualizar(self, nota: NotaDeDrift) -> None:
        self.banco.executar(
            "update notas_drift set texto = :texto, atualizado_em = now() where id = :id",
            id=nota.id, texto=nota.texto,
        )

    # ---- Delete: herdado de RepositorioBase
