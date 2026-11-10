"""Telas do CRUD de Manutenção.

O gestor dispara (Create) a partir de um desvio, edita e exclui.
O técnico vê a lista e conclui (Update) escrevendo as observações.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request

from driftor.analises.repositorio import RepositorioDeAnalises
from driftor.dominio import Manutencao
from driftor.manutencoes.eventos import publicador_de_manutencao
from driftor.manutencoes.repositorio import RepositorioDeManutencoes
from driftor.telas import exigir, ir_para, tela

rotas = APIRouter()


# ---- Read: lista (gestor e técnico)
@rotas.get("/manutencoes", dependencies=[Depends(exigir("manutencoes"))])
def listar(request: Request):
    return tela(request, "manutencoes/lista.html", manutencoes=RepositorioDeManutencoes().listar_resumo())


# ---- Create: o gestor dispara a manutenção na tela da análise
@rotas.post("/analises/{analise_id}/manutencoes", dependencies=[Depends(exigir("disparar_manutencao"))])
def disparar(analise_id: str, drift_id: str = Form(""), descricao: str = Form("")):
    analise = RepositorioDeAnalises().obter_ou_erro(analise_id)
    manutencao = Manutencao.disparar(analise, drift_id, descricao)
    RepositorioDeManutencoes().inserir(manutencao)
    publicador_de_manutencao.notificar("manutencao_disparada", {  # Observer: avisa o técnico
        "mensagem": f"Nova manutenção: {manutencao.descricao} (análise “{analise.nome}”).",
    })
    return ir_para(f"/analises/{analise_id}")


# ---- Read: detalhe (gestor e técnico)
@rotas.get("/manutencoes/{id}", dependencies=[Depends(exigir("manutencoes"))])
def ver(request: Request, id: str):
    manutencao = RepositorioDeManutencoes().obter_ou_erro(id)
    analise = RepositorioDeAnalises().obter_ou_erro(manutencao.analise_id)
    drift = next((d for d in analise.drifts if d.id == manutencao.drift_id), None)
    return tela(request, "manutencoes/detalhe.html", manutencao=manutencao, analise=analise, drift=drift)


# ---- Update pelo técnico: concluir com observações
@rotas.post("/manutencoes/{id}/concluir", dependencies=[Depends(exigir("concluir_manutencao"))])
def concluir(id: str, observacoes: str = Form("")):
    repo = RepositorioDeManutencoes()
    manutencao = repo.obter_ou_erro(id)
    manutencao.concluir(observacoes)
    repo.atualizar(manutencao)
    publicador_de_manutencao.notificar("manutencao_concluida", {  # Observer: avisa o gestor
        "mensagem": f"Manutenção concluída pelo técnico: {manutencao.descricao}.",
    })
    return ir_para("/manutencoes")


# ---- Update pelo gestor: corrigir a descrição enquanto está pendente
@rotas.post("/manutencoes/{id}", dependencies=[Depends(exigir("disparar_manutencao"))])
def editar(id: str, descricao: str = Form("")):
    repo = RepositorioDeManutencoes()
    manutencao = repo.obter_ou_erro(id)
    manutencao.editar(descricao)
    repo.atualizar(manutencao)
    return ir_para(f"/manutencoes/{id}")


# ---- Delete pelo gestor
@rotas.post("/manutencoes/{id}/excluir", dependencies=[Depends(exigir("disparar_manutencao"))])
def excluir(id: str):
    RepositorioDeManutencoes().excluir(id)
    return ir_para("/manutencoes")
