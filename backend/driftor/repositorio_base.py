"""COMPACTAÇÃO DE CÓDIGO: o que os quatro repositórios faziam igual agora está aqui uma vez só.

Cada repositório diz só a sua tabela, as suas colunas e como transformar uma linha
do banco em objeto do domínio. Ler um, ler todos, achar-ou-dar-erro e excluir são
herdados desta classe.
"""

from __future__ import annotations

from typing import Generic, TypeVar

from driftor.banco import BancoDeDados
from driftor.dominio import ErroDeNegocio

T = TypeVar("T")


class RepositorioBase(Generic[T]):
    tabela: str = ""
    colunas: str = "*"
    ordem: str = "id"
    nome_no_singular: str = "registro"

    def __init__(self) -> None:
        self.banco = BancoDeDados()

    def criar_objeto(self, linha: dict) -> T:
        raise NotImplementedError

    # ---- Read
    def listar(self) -> list[T]:
        linhas = self.banco.consultar(f"select {self.colunas} from {self.tabela} order by {self.ordem}")
        return [self.criar_objeto(linha) for linha in linhas]

    def obter(self, id: str) -> T | None:
        linha = self.banco.consultar_um(f"select {self.colunas} from {self.tabela} where id = :id", id=id)
        return self.criar_objeto(linha) if linha else None

    def obter_ou_erro(self, id: str) -> T:
        objeto = self.obter(id)
        if objeto is None:
            raise ErroDeNegocio(f"{self.nome_no_singular.capitalize()} não encontrado(a).")
        return objeto

    # ---- Delete
    def excluir(self, id: str) -> None:
        self.banco.executar(f"delete from {self.tabela} where id = :id", id=id)
