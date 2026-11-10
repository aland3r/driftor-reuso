"""Telas do CRUD de Atividade (Alander): o catálogo usado no mapeamento dos logs."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request

from driftor.atividades.repositorio import RepositorioDeAtividades
from driftor.dominio import Atividade, ErroDeNegocio
from driftor.telas import exigir_recurso, ir_para, tela

rotas = APIRouter(dependencies=[Depends(exigir_recurso("atividades"))])


def _atividade_ou_erro(repo: RepositorioDeAtividades, id: str) -> Atividade:
    atividade = repo.obter(id)
    if atividade is None:
        raise ErroDeNegocio("Atividade não encontrada.")
    return atividade


# ---- Read
@rotas.get("/atividades")
def listar(request: Request):
    return tela(request, "atividades/lista.html", atividades=RepositorioDeAtividades().listar())


# ---- Create
@rotas.post("/atividades")
def criar(nome: str = Form(""), descricao: str = Form("")):
    RepositorioDeAtividades().inserir(Atividade.criar(nome, descricao))
    return ir_para("/atividades")


# ---- Update
@rotas.get("/atividades/{id}/editar")
def editar(request: Request, id: str):
    atividade = _atividade_ou_erro(RepositorioDeAtividades(), id)
    return tela(request, "atividades/editar.html", atividade=atividade)


@rotas.post("/atividades/{id}")
def salvar(id: str, nome: str = Form(""), descricao: str = Form("")):
    repo = RepositorioDeAtividades()
    atividade = _atividade_ou_erro(repo, id)
    atividade.editar(nome, descricao)
    repo.atualizar(atividade)
    return ir_para("/atividades")


# ---- Delete
@rotas.post("/atividades/{id}/excluir")
def excluir(id: str):
    RepositorioDeAtividades().excluir(id)
    return ir_para("/atividades")
