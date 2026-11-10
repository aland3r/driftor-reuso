"""Leitura do log de eventos (.xes ou .csv), reaproveitada do serviço de mineração do Driftor.

Converte o arquivo em Traces do domínio. XES passa pelo PM4Py, que junta os pares
start/complete num evento só, com duração. CSV é o formato do chão de fábrica
(colunas Case;Atividade;Inicio;Fim;Tempo(s)).
"""

from __future__ import annotations

import io
import os
import tempfile

import pandas as pd

from driftor.dominio import ErroDeNegocio, Evento, Trace


def ler_log(conteudo: bytes, arquivo: str) -> tuple[str, list[Trace]]:
    """Devolve o formato ('xes' ou 'csv') e os traces do log."""
    if not conteudo:
        raise ErroDeNegocio("O arquivo está vazio.")
    nome = arquivo.lower()
    if nome.endswith(".xes"):
        return "xes", _para_traces(_tabela_xes(conteudo))
    if nome.endswith(".csv"):
        return "csv", _para_traces(_tabela_csv(conteudo))
    raise ErroDeNegocio("Envie um arquivo .xes ou .csv.")


def _tabela_xes(conteudo: bytes) -> pd.DataFrame:
    import pm4py
    from pm4py.objects.log.util import interval_lifecycle

    descritor, caminho = tempfile.mkstemp(suffix=".xes")
    try:
        with os.fdopen(descritor, "wb") as temporario:
            temporario.write(conteudo)
        try:
            log = pm4py.read_xes(caminho)
        except Exception as erro:  # noqa: BLE001
            raise ErroDeNegocio(f"Não foi possível ler o XES: {erro}") from erro
    finally:
        try:
            os.unlink(caminho)
        except OSError:
            pass
    # start/complete viram um evento só, com a duração em @@duration
    log = interval_lifecycle.to_interval(pm4py.convert_to_event_log(log))
    df = pm4py.convert_to_dataframe(log)
    return pd.DataFrame({
        "case_id": df["case:concept:name"].astype(str),
        "rotulo": df["concept:name"].astype(str),
        "inicio": pd.to_datetime(df["time:timestamp"], utc=True, errors="coerce"),
        "duracao_s": pd.to_numeric(df.get("@@duration"), errors="coerce"),
    })


def _tabela_csv(conteudo: bytes) -> pd.DataFrame:
    try:
        df = pd.read_csv(io.BytesIO(conteudo), sep=";", encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(io.BytesIO(conteudo), sep=";", encoding="latin-1")
    df.columns = [str(c).strip() for c in df.columns]
    faltando = [c for c in ("Case", "Atividade", "Inicio") if c not in df.columns]
    if faltando:
        raise ErroDeNegocio("O CSV precisa das colunas Case;Atividade;Inicio;Fim;Tempo(s).")
    inicio = pd.to_datetime(df["Inicio"], format="%d-%m-%Y %H:%M:%S", utc=True, errors="coerce")
    if "Tempo(s)" in df.columns:
        duracao = pd.to_numeric(df["Tempo(s)"], errors="coerce")
    else:
        fim = pd.to_datetime(df["Fim"], format="%d-%m-%Y %H:%M:%S", utc=True, errors="coerce")
        duracao = (fim - inicio).dt.total_seconds()
    return pd.DataFrame({
        "case_id": df["Case"].astype(str),
        "rotulo": df["Atividade"].astype(str).str.strip(),
        "inicio": inicio,
        "duracao_s": duracao,
    })


def _para_traces(tabela: pd.DataFrame) -> list[Trace]:
    tabela = tabela.dropna(subset=["case_id", "rotulo"])
    tabela = tabela[tabela["rotulo"].str.len() > 0]
    if tabela.empty:
        raise ErroDeNegocio("O arquivo não tem nenhum evento legível.")
    tabela = tabela.sort_values(by=["case_id", "inicio"], na_position="last", kind="stable")
    traces = []
    for case_id, grupo in tabela.groupby("case_id", sort=False):
        eventos = [
            Evento(
                rotulo=str(linha.rotulo),
                inicio=None if pd.isna(linha.inicio) else linha.inicio.to_pydatetime(),
                duracao_s=None if pd.isna(linha.duracao_s) else float(linha.duracao_s),
            )
            for linha in grupo.itertuples(index=False)
        ]
        traces.append(Trace(case_id=str(case_id), eventos=eventos))
    return traces
