"""Entrada simulada (sem senha): a pessoa escolhe o perfil Gestor ou Técnico de manutenção.

O papel fica num cookie. É ele que liga a VARIABILIDADE por papel (config.PAPEIS).
"""

from __future__ import annotations

from fastapi import APIRouter, Form, Request

from driftor.config import PAPEIS
from driftor.dominio import ErroDeNegocio
from driftor.telas import ir_para, papel_atual, tela

rotas = APIRouter()


@rotas.get("/")
def inicio(request: Request):
    papel = papel_atual(request)
    return ir_para(PAPEIS[papel]["inicio"] if papel else "/entrar")


@rotas.get("/entrar")
def escolher_perfil(request: Request):
    return tela(request, "entrar.html")


@rotas.post("/entrar")
def entrar(papel: str = Form("")):
    if papel not in PAPEIS:
        raise ErroDeNegocio("Escolha um perfil.")
    resposta = ir_para(PAPEIS[papel]["inicio"])
    resposta.set_cookie("papel", papel, httponly=True, samesite="lax")
    return resposta


@rotas.get("/sair")
def sair():
    resposta = ir_para("/entrar")
    resposta.delete_cookie("papel")
    return resposta
