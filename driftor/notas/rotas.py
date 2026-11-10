"""Telas do CRUD de Nota de drift (Emanuelle): anotar o que aconteceu em cada desvio."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request

from driftor.analises.repositorio import RepositorioDeAnalises
from driftor.dominio import ErroDeNegocio, NotaDeDrift
from driftor.notas.eventos import publicador_de_notas
from driftor.notas.repositorio import RepositorioDeNotas
from driftor.telas import exigir_recurso, ir_para, tela

rotas = APIRouter(dependencies=[Depends(exigir_recurso("notas"))])


def _analise_do_drift(drift_id: str) -> str:
    linha = RepositorioDeNotas().banco.consultar_um("select analise_id from drifts where id = :id", id=drift_id)
    if linha is None:
        raise ErroDeNegocio("Desvio não encontrado.")
    return str(linha["analise_id"])


def _nota_ou_erro(repo: RepositorioDeNotas, id: str) -> NotaDeDrift:
    nota = repo.obter(id)
    if nota is None:
        raise ErroDeNegocio("Nota não encontrada.")
    return nota


# ---- Read: notas de todos os desvios de uma análise
@rotas.get("/analises/{analise_id}/notas")
def listar(request: Request, analise_id: str):
    analise = RepositorioDeAnalises().obter(analise_id)
    if analise is None:
        raise ErroDeNegocio("Análise não encontrada.")
    return tela(request, "notas/lista.html", analise=analise,
                notas=RepositorioDeNotas().listar_da_analise(analise_id))


# ---- Create
@rotas.post("/notas")
def criar(drift_id: str = Form(""), texto: str = Form("")):
    nota = NotaDeDrift.criar(drift_id, texto)
    analise_id = _analise_do_drift(drift_id)
    RepositorioDeNotas().inserir(nota)
    publicador_de_notas.notificar("nota_criada", {"analise_id": analise_id, "mensagem": "Nota salva."})  # Observer
    return ir_para(f"/analises/{analise_id}/notas")


# ---- Update
@rotas.get("/notas/{id}/editar")
def editar(request: Request, id: str):
    nota = _nota_ou_erro(RepositorioDeNotas(), id)
    return tela(request, "notas/editar.html", nota=nota, analise_id=_analise_do_drift(nota.drift_id))


@rotas.post("/notas/{id}")
def salvar(id: str, texto: str = Form("")):
    repo = RepositorioDeNotas()
    nota = _nota_ou_erro(repo, id)
    nota.editar(texto)
    repo.atualizar(nota)
    return ir_para(f"/analises/{_analise_do_drift(nota.drift_id)}/notas")


# ---- Delete
@rotas.post("/notas/{id}/excluir")
def excluir(id: str):
    repo = RepositorioDeNotas()
    nota = _nota_ou_erro(repo, id)
    analise_id = _analise_do_drift(nota.drift_id)
    repo.excluir(id)
    publicador_de_notas.notificar("nota_excluida", {"analise_id": analise_id, "mensagem": "Nota excluída."})  # Observer
    return ir_para(f"/analises/{analise_id}/notas")
