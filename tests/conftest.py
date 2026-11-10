"""Os testes usam um Postgres local (DATABASE_URL) e limpam o schema antes de cada teste."""

import os

import pytest

os.environ.setdefault("DATABASE_URL", "postgresql://driftor_reuso:local@localhost:5432/driftor")

from fastapi.testclient import TestClient  # noqa: E402

from driftor.banco import BancoDeDados  # noqa: E402
from driftor.main import app  # noqa: E402


@pytest.fixture()
def cliente():
    banco = BancoDeDados()
    banco.aplicar_schema()
    banco.executar("truncate processos, atividades cascade")
    with TestClient(app) as c:
        yield c
