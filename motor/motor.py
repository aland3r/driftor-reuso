"""Motor de mineração (Python): lê o log XES, descobre o grafo com o PM4Py e detecta desvios com o ADWIN.

O backend Java chama estes três endpoints pelos seus Adapters. Não guarda nada.
"""

import tempfile

import pandas as pd
import pm4py
from fastapi import FastAPI, UploadFile
from pm4py.objects.log.util import interval_lifecycle
from pydantic import BaseModel
from river.drift import ADWIN

app = FastAPI()


@app.post("/log")
async def ler_log(arquivo: UploadFile):
    """Cada par start/complete vira um evento com início e duração em segundos."""
    with tempfile.NamedTemporaryFile(suffix=".xes") as f:
        f.write(await arquivo.read())
        f.flush()
        log = interval_lifecycle.to_interval(pm4py.convert_to_event_log(pm4py.read_xes(f.name)))
    return [
        {"caseId": str(t.attributes["concept:name"]), "eventos": [
            {"atividade": e["concept:name"], "inicio": e["time:timestamp"].isoformat(), "duracao": e["@@duration"]}
            for e in t]}
        for t in log
    ]


class Sequencias(BaseModel):
    traces: list[list[str]]


@app.post("/dfg")
def descobrir_dfg(corpo: Sequencias):
    tabela = pd.DataFrame([
        {"case": str(i), "atividade": a, "momento": pd.Timestamp(p, unit="s", tz="UTC")}
        for i, t in enumerate(corpo.traces) for p, a in enumerate(t)
    ])
    dfg, _, _ = pm4py.discover_dfg(tabela, case_id_key="case", activity_key="atividade", timestamp_key="momento")
    return [{"de": de, "para": para, "vezes": int(n)} for (de, para), n in dfg.items()]


class Serie(BaseModel):
    valores: list[float]
    delta: float


@app.post("/adwin")
def detectar(corpo: Serie):
    """Para cada desvio, o ponto onde a janela que sobrou no ADWIN começa (início da mudança)."""
    adwin, inicios = ADWIN(delta=corpo.delta), [0]
    for i, valor in enumerate(corpo.valores):
        adwin.update(valor)
        if adwin.drift_detected:
            inicios.append(max(i - int(adwin.width) + 1, inicios[-1] + 1))
    return {"inicios": inicios[1:]}
