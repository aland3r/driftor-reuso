"""Ponto de entrada do Driftor (Reuso): monta o app, liga os observadores e aplica a variabilidade."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from driftor.analises import rotas as analises
from driftor.analises.eventos import AtualizadorDoProcesso, publicador_de_analise
from driftor.atividades import rotas as atividades
from driftor.banco import BancoDeDados
from driftor.config import Configuracao
from driftor.dominio import ErroDeNegocio
from driftor.notas import rotas as notas
from driftor.notas.eventos import ContadorDeNotas, publicador_de_notas
from driftor.observador import aviso_na_tela
from driftor.processos import rotas as processos
from driftor.telas import ir_para, tela


@asynccontextmanager
async def ao_subir(_app: FastAPI):
    BancoDeDados().aplicar_schema()  # cria as tabelas do schema.sql, se ainda não existem
    yield


app = FastAPI(title="Driftor", lifespan=ao_subir)
app.mount("/static", StaticFiles(directory=Path(__file__).with_name("static")), name="static")

# OBSERVER: quem reage a cada evento é decidido aqui, não dentro de quem publica.
publicador_de_analise.inscrever(AtualizadorDoProcesso())
publicador_de_analise.inscrever(aviso_na_tela)
publicador_de_notas.inscrever(ContadorDeNotas())
publicador_de_notas.inscrever(aviso_na_tela)

# VARIABILIDADE: as rotas de todos os recursos existem, mas cada uma confere a edição.
for modulo in (processos, atividades, analises, notas):
    app.include_router(modulo.rotas)


@app.get("/")
def inicio():
    return ir_para("/processos")


@app.get("/saude")
def saude():
    return {"ok": True, "edicao": Configuracao().edicao}


@app.exception_handler(ErroDeNegocio)
def erro_de_negocio(request: Request, erro: ErroDeNegocio):
    resposta = tela(request, "erro.html", mensagem=str(erro), voltar=request.headers.get("referer", "/"))
    resposta.status_code = 422
    return resposta
