"""Acesso ao banco do CRUD de Atividade: tabela atividades."""

from __future__ import annotations

from sqlalchemy.exc import IntegrityError

from driftor.banco import BancoDeDados
from driftor.dominio import Atividade, ErroDeNegocio


def _para_atividade(linha: dict) -> Atividade:
    return Atividade(id=str(linha["id"]), nome=linha["nome"], descricao=linha["descricao"])


class RepositorioDeAtividades:
    def __init__(self) -> None:
        self.banco = BancoDeDados()

    # ---- Read
    def listar(self) -> list[Atividade]:
        linhas = self.banco.consultar("select id, nome, descricao from atividades order by nome")
        return [_para_atividade(linha) for linha in linhas]

    def obter(self, id: str) -> Atividade | None:
        linha = self.banco.consultar_um("select id, nome, descricao from atividades where id = :id", id=id)
        return _para_atividade(linha) if linha else None

    def obter_por_nome(self, nome: str) -> Atividade | None:
        linha = self.banco.consultar_um(
            "select id, nome, descricao from atividades where lower(nome) = lower(:nome)", nome=nome
        )
        return _para_atividade(linha) if linha else None

    # ---- Create
    def inserir(self, atividade: Atividade) -> None:
        try:
            self.banco.executar(
                "insert into atividades (id, nome, descricao) values (:id, :nome, :descricao)",
                id=atividade.id, nome=atividade.nome, descricao=atividade.descricao,
            )
        except IntegrityError as erro:
            raise ErroDeNegocio(f"Já existe uma atividade chamada {atividade.nome}.") from erro

    # ---- Update
    def atualizar(self, atividade: Atividade) -> None:
        try:
            self.banco.executar(
                "update atividades set nome = :nome, descricao = :descricao where id = :id",
                id=atividade.id, nome=atividade.nome, descricao=atividade.descricao,
            )
        except IntegrityError as erro:
            raise ErroDeNegocio(f"Já existe uma atividade chamada {atividade.nome}.") from erro

    # ---- Delete (o banco recusa se algum processo usa a atividade: on delete restrict)
    def excluir(self, id: str) -> None:
        try:
            self.banco.executar("delete from atividades where id = :id", id=id)
        except IntegrityError as erro:
            raise ErroDeNegocio("Esta atividade está mapeada em um processo e não pode ser excluída.") from erro
