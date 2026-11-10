"""Telas do CRUD de Processo (Alander): criar, ver, carregar log, mapear, renomear e excluir."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile

from driftor.analises.repositorio import RepositorioDeAnalises
from driftor.atividades.repositorio import RepositorioDeAtividades
from driftor.config import Configuracao
from driftor.dominio import Atividade, ErroDeNegocio, Grafo, Operacao, Processo, Variante
from driftor.mineracao.grafo import MineradorDeGrafo, Pm4pyMineradorAdapter
from driftor.mineracao.leitor_log import ler_log
from driftor.processos.repositorio import RepositorioDeProcessos
from driftor.telas import exigir_recurso, ir_para, tela

rotas = APIRouter(dependencies=[Depends(exigir_recurso("processos"))])


def minerador() -> MineradorDeGrafo:
    return Pm4pyMineradorAdapter()


def _processo_ou_erro(repo: RepositorioDeProcessos, id: str) -> Processo:
    processo = repo.obter(id)
    if processo is None:
        raise ErroDeNegocio("Processo não encontrado.")
    return processo


# ---- Read: lista de processos (tela inicial)
@rotas.get("/processos")
def listar(request: Request):
    return tela(request, "processos/lista.html", processos=RepositorioDeProcessos().listar())


# ---- Create: só o nome; o log vem depois, na página do processo
@rotas.post("/processos")
def criar(nome: str = Form("")):
    processo = Processo.criar(nome)
    RepositorioDeProcessos().inserir(processo)
    return ir_para(f"/processos/{processo.id}")


# ---- Read: detalhe do processo (grafo, variantes e análises)
@rotas.get("/processos/{id}")
def ver(request: Request, id: str, minerador: MineradorDeGrafo = Depends(minerador)):
    repo = RepositorioDeProcessos()
    processo = _processo_ou_erro(repo, id)
    if processo.status == "mapeando":
        return ir_para(f"/processos/{id}/operacoes")
    grafo, variantes, analises, atividades = None, [], [], []
    if processo.pode_analisar():
        traces = repo.traces(id)
        grafo = Grafo.montar(traces, minerador.descobrir_arestas(traces))  # Adapter em uso
        variantes = Variante.agrupar(traces)
        atividades = [no.atividade for no in grafo.nos]
        if Configuracao().tem_recurso("analises"):
            analises = RepositorioDeAnalises().listar(processo_id=id)
    return tela(request, "processos/detalhe.html", processo=processo, grafo=grafo,
                variantes=variantes, analises=analises, atividades=atividades)


# ---- Update: carregar o log de eventos no processo
@rotas.post("/processos/{id}/log")
async def carregar_log(id: str, arquivo: UploadFile = File(...)):
    repo = RepositorioDeProcessos()
    processo = _processo_ou_erro(repo, id)
    formato, traces = ler_log(await arquivo.read(), arquivo.filename or "")
    processo.carregar_log(arquivo.filename or "", formato, traces)
    repo.substituir_log(processo, traces, Operacao.contar(traces))
    return ir_para(f"/processos/{id}/operacoes")


# ---- Update: mapear cada operação do log para uma atividade do catálogo
@rotas.get("/processos/{id}/operacoes")
def mapear_operacoes(request: Request, id: str):
    repo = RepositorioDeProcessos()
    processo = _processo_ou_erro(repo, id)
    catalogo = RepositorioDeAtividades().listar()
    operacoes = repo.operacoes(id)
    for operacao in operacoes:
        operacao.atividade = operacao.atividade or operacao.sugerir_atividade(catalogo)
    return tela(request, "processos/operacoes.html", processo=processo, operacoes=operacoes, catalogo=catalogo)


@rotas.post("/processos/{id}/operacoes")
async def salvar_operacoes(request: Request, id: str):
    repo = RepositorioDeProcessos()
    processo = _processo_ou_erro(repo, id)
    formulario = await request.form()
    atividades = RepositorioDeAtividades()
    ligacoes: dict[str, str] = {}
    for operacao in repo.operacoes(id):
        operacao.mapear(str(formulario.get(f"op::{operacao.rotulo}", "")))
        atividade = atividades.obter_por_nome(operacao.atividade)
        if atividade is None:  # nome novo entra no catálogo
            atividade = Atividade.criar(operacao.atividade)
            atividades.inserir(atividade)
        ligacoes[operacao.rotulo] = atividade.id
    repo.salvar_mapeamento(id, ligacoes)
    processo.marcar_pronto()
    repo.atualizar(processo)
    return ir_para(f"/processos/{id}")


# ---- Update: renomear
@rotas.post("/processos/{id}/renomear")
def renomear(id: str, nome: str = Form("")):
    repo = RepositorioDeProcessos()
    processo = _processo_ou_erro(repo, id)
    processo.renomear(nome)
    repo.atualizar(processo)
    return ir_para(f"/processos/{id}")


# ---- Delete
@rotas.post("/processos/{id}/excluir")
def excluir(id: str):
    RepositorioDeProcessos().excluir(id)
    return ir_para("/processos")
