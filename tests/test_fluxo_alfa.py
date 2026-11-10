"""Fluxo completo com os quatro logs da Alfa: os desvios do artigo (0, 4, 7 e 9) precisam aparecer."""

import re
from pathlib import Path

import pytest

DATASETS = Path(__file__).resolve().parents[1] / "exemplos"


def _id_na_url(resposta) -> str:
    return re.search(r"/([0-9a-f-]{36})", resposta.headers["location"]).group(1)


@pytest.mark.parametrize("arquivo, esperados", [("ST_20.xes", 0), ("DR_20.xes", 4), ("DR_MS_20.xes", 7), ("DR_MS_ST_20.xes", 9)])
def test_desvios_do_artigo(cliente, arquivo, esperados):
    criado = cliente.post("/processos", data={"nome": arquivo}, follow_redirects=False)
    processo_id = _id_na_url(criado)

    with open(DATASETS / arquivo, "rb") as f:
        cliente.post(f"/processos/{processo_id}/log", files={"arquivo": (arquivo, f.read())}, follow_redirects=False)
    tela = cliente.get(f"/processos/{processo_id}/operacoes").text
    rotulos = re.findall(r'name="op::([^"]+)" value="([^"]*)"', tela)
    assert ("Machine_Operating", "Machine_Operating") in rotulos
    cliente.post(f"/processos/{processo_id}/operacoes", data={f"op::{r}": v for r, v in rotulos}, follow_redirects=False)

    assert "flowchart LR" in cliente.get(f"/processos/{processo_id}").text
    analise = cliente.post(f"/processos/{processo_id}/analises",
                           data={"atividade": "Machine_Operating", "delta": "0.002", "tratamento": "bruto"},
                           follow_redirects=False)
    tela = cliente.get(analise.headers["location"]).text
    assert f"Desvios encontrados ({esperados})" in tela
    assert "concluída" in tela  # aviso do Observer
