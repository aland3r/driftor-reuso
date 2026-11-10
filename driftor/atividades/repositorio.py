"""Acesso ao banco do CRUD de Atividade: tabela atividades."""

from __future__ import annotations

from sqlalchemy.exc import IntegrityError

from driftor.dominio import Atividade, ErroDeNegocio
from driftor.repositorio_base import RepositorioBase


class RepositorioDeAtividades(RepositorioBase[Atividade]):
    # listar, obter e obter_ou_erro vêm de RepositorioBase
    tabela = "atividades"
    colunas = "id, nome, descricao"
    ordem = "nome"
    nome_no_singular = "atividade"

    def criar_objeto(self, linha: dict) -> Atividade:
        return Atividade(id=str(linha["id"]), nome=linha["nome"], descricao=linha["descricao"])

    # ---- Read
    def obter_por_nome(self, nome: str) -> Atividade | None:
        linha = self.banco.consultar_um(
            f"select {self.colunas} from atividades where lower(nome) = lower(:nome)", nome=nome
        )
        return self.criar_objeto(linha) if linha else None

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
            super().excluir(id)
        except IntegrityError as erro:
            raise ErroDeNegocio("Esta atividade está mapeada em um processo e não pode ser excluída.") from erro
