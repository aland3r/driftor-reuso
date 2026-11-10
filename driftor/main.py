"""Ponto de entrada do Driftor (Reuso): monta o app, liga os observadores e aplica a variabilidade."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from driftor import acesso
from driftor.analises import rotas as analises
from driftor.analises.eventos import AtualizadorDoProcesso, publicador_de_analise
from driftor.atividades import rotas as atividades
from driftor.banco import BancoDeDados
from driftor.dominio import ErroDeNegocio
from driftor.manutencoes import rotas as manutencoes
from driftor.manutencoes.eventos import publicador_de_manutencao
from driftor.observador import avisos_por_papel
from driftor.processos import rotas as processos
from driftor.telas import PrecisaEntrar, SemPermissao, ir_para, tela


@asynccontextmanager
async def ao_subir(_app: FastAPI):
    BancoDeDados().aplicar_schema()  # cria as tabelas do schema.sql, se ainda não existem
    yield


app = FastAPI(title="Driftor", lifespan=ao_subir)
app.mount("/static", StaticFiles(directory=Path(__file__).with_name("static")), name="static")

# OBSERVER: quem reage a cada evento é decidido aqui, não dentro de quem publica.
publicador_de_analise.inscrever(AtualizadorDoProcesso())
publicador_de_analise.inscrever(avisos_por_papel["gestor"])
publicador_de_manutencao.inscrever(avisos_por_papel["tecnico"])  # recebe "manutencao_disparada"
publicador_de_manutencao.inscrever(avisos_por_papel["gestor"])   # recebe "manutencao_concluida"

# VARIABILIDADE: todas as rotas existem; cada uma confere o papel de quem entrou (telas.exigir).
for modulo in (acesso, processos, atividades, analises, manutencoes):
    app.include_router(modulo.rotas)


@app.get("/saude")
def saude():
    return {"ok": True}


@app.exception_handler(PrecisaEntrar)
def precisa_entrar(_request: Request, _erro: PrecisaEntrar):
    return ir_para("/entrar")


@app.exception_handler(SemPermissao)
def sem_permissao(request: Request, _erro: SemPermissao):
    resposta = tela(request, "erro.html", mensagem="Este perfil não tem acesso a esta tela.", voltar="/")
    resposta.status_code = 403
    return resposta


@app.exception_handler(ErroDeNegocio)
def erro_de_negocio(request: Request, erro: ErroDeNegocio):
    resposta = tela(request, "erro.html", mensagem=str(erro), voltar=request.headers.get("referer", "/"))
    resposta.status_code = 422
    return resposta
