"""Os quatro logs da Alfa precisam dar os desvios do artigo: 0, 4, 7 e 9."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from motor import app

EXEMPLOS = Path(__file__).resolve().parents[1] / "exemplos"


@pytest.mark.parametrize("arquivo, esperados", [("ST_20.xes", 0), ("DR_20.xes", 4), ("DR_MS_20.xes", 7), ("DR_MS_ST_20.xes", 9)])
def test_desvios_do_artigo(arquivo, esperados):
    cliente = TestClient(app)
    traces = cliente.post("/log", files={"arquivo": (arquivo, (EXEMPLOS / arquivo).read_bytes())}).json()
    traces.sort(key=lambda t: min(e["inicio"] for e in t["eventos"]))
    valores = [sum(e["duracao"] for e in t["eventos"] if e["atividade"] == "Machine_Operating") for t in traces]
    assert len(cliente.post("/adwin", json={"valores": valores, "delta": 0.002}).json()["inicios"]) == esperados
    assert cliente.post("/dfg", json={"traces": [[e["atividade"] for e in t["eventos"]] for t in traces]}).json()
