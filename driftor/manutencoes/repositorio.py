"""Acesso ao banco do CRUD de Manutenção: tabela manutencoes."""

from __future__ import annotations

from driftor.dominio import Manutencao
from driftor.repositorio_base import RepositorioBase


class RepositorioDeManutencoes(RepositorioBase[Manutencao]):
    # obter, obter_ou_erro e excluir vêm de RepositorioBase
    tabela = "manutencoes"
    colunas = "id, analise_id, drift_id, descricao, status, observacoes, criado_em, concluida_em"
    nome_no_singular = "manutenção"

    def criar_objeto(self, linha: dict) -> Manutencao:
        return Manutencao(**{
            **linha,
            "id": str(linha["id"]),
            "analise_id": str(linha["analise_id"]),
            "drift_id": str(linha["drift_id"]) if linha["drift_id"] else None,
        })

    # ---- Read: a lista com o nome da análise, do processo e o número do desvio
    def listar_resumo(self, analise_id: str | None = None) -> list[dict]:
        filtro = "where m.analise_id = :analise_id" if analise_id else ""
        return self.banco.consultar(
            f"""select m.id, m.descricao, m.status, m.observacoes, m.criado_em, m.concluida_em,
                       a.id as analise_id, a.nome as analise, p.nome as processo, d.posicao as desvio
                from manutencoes m
                join analises a on a.id = m.analise_id
                join processos p on p.id = a.processo_id
                left join drifts d on d.id = m.drift_id
                {filtro}
                order by (m.status = 'pendente') desc, m.criado_em desc""",
            analise_id=analise_id,
        )

    def contar_pendentes(self) -> int:
        return self.banco.consultar_um("select count(*) as n from manutencoes where status = 'pendente'")["n"]

    # ---- Create
    def inserir(self, manutencao: Manutencao) -> None:
        self.banco.executar(
            """insert into manutencoes (id, analise_id, drift_id, descricao)
               values (:id, :analise_id, :drift_id, :descricao)""",
            id=manutencao.id, analise_id=manutencao.analise_id,
            drift_id=manutencao.drift_id, descricao=manutencao.descricao,
        )

    # ---- Update (o gestor edita a descrição; o técnico conclui com observações)
    def atualizar(self, manutencao: Manutencao) -> None:
        self.banco.executar(
            """update manutencoes set descricao = :descricao, status = :status, observacoes = :observacoes,
                   concluida_em = case when :status = 'concluida' then coalesce(concluida_em, now()) end
               where id = :id""",
            id=manutencao.id, descricao=manutencao.descricao,
            status=manutencao.status, observacoes=manutencao.observacoes,
        )

    # ---- Delete: herdado de RepositorioBase
