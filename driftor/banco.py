"""PADRÃO SINGLETON, exemplo 2: BancoDeDados.

Abre UMA conexão com o Postgres (um pool do SQLAlchemy) para o app inteiro.
Todos os repositórios chamam BancoDeDados() e recebem o mesmo objeto, em vez de
cada tela abrir sua própria conexão.
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from driftor.config import Configuracao

SCHEMA_SQL = Path(__file__).with_name("schema.sql")


class BancoDeDados:
    _instancia: BancoDeDados | None = None

    def __new__(cls) -> BancoDeDados:
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            url = Configuracao().url_do_banco.replace("postgresql://", "postgresql+psycopg://", 1)
            cls._instancia.engine: Engine = create_engine(url, pool_pre_ping=True)
        return cls._instancia

    def consultar(self, sql: str, **parametros) -> list[dict]:
        """SELECT: devolve as linhas como dicionários."""
        with self.engine.connect() as conexao:
            return [dict(linha._mapping) for linha in conexao.execute(text(sql), parametros)]

    def consultar_um(self, sql: str, **parametros) -> dict | None:
        linhas = self.consultar(sql, **parametros)
        return linhas[0] if linhas else None

    def executar(self, sql: str, **parametros) -> int:
        """INSERT, UPDATE ou DELETE numa transação. Devolve quantas linhas mudaram."""
        with self.engine.begin() as conexao:
            return conexao.execute(text(sql), parametros).rowcount

    def executar_varios(self, sql: str, linhas: list[dict]) -> None:
        """O mesmo INSERT para muitas linhas de uma vez (eventos do log)."""
        if linhas:
            with self.engine.begin() as conexao:
                conexao.execute(text(sql), linhas)

    def aplicar_schema(self) -> None:
        with self.engine.begin() as conexao:
            conexao.exec_driver_sql(SCHEMA_SQL.read_text(encoding="utf-8"))
