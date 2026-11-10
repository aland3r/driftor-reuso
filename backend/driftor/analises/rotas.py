"""Telas do CRUD de Análise: gerar a análise de desvios, ver, renomear e excluir."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request

from driftor.analises.eventos import publicador_de_analise
from driftor.analises.repositorio import RepositorioDeAnalises
from driftor.dominio import Analise, ErroDeNegocio, PontoDaSerie
from driftor.mineracao.detector import DetectorDeDrift, RiverAdwinAdapter, suavizar
from driftor.processos.repositorio import RepositorioDeProcessos
from driftor.manutencoes.repositorio import RepositorioDeManutencoes
from driftor.telas import exigir, ir_para, tela

rotas = APIRouter()
so_gestor = [Depends(exigir("analises"))]


def detector() -> DetectorDeDrift:
    return RiverAdwinAdapter()


# ---- Read: todas as análises
@rotas.get("/analises", dependencies=so_gestor)
def listar(request: Request):
    return tela(request, "analises/lista.html", analises=RepositorioDeAnalises().listar_resumo())


# ---- Create: botão "Gerar análise de desvios" na página do processo
@rotas.post("/processos/{processo_id}/analises", dependencies=so_gestor)
def criar(
    processo_id: str,
    nome: str = Form(""),
    atividade: str = Form(""),
    delta: float = Form(0.002),
    tratamento: str = Form("bruto"),
    detector: DetectorDeDrift = Depends(detector),
):
    processos = RepositorioDeProcessos()
    processo = processos.obter_ou_erro(processo_id)
    analise = Analise.criar(processo, nome, delta, tratamento, atividade)

    pontos = PontoDaSerie.serie_de_duracao(processos.traces(processo_id), analise.atividade)
    if len(pontos) < 2:
        raise ErroDeNegocio("A série tem menos de duas observações.")
    valores = [p.valor for p in pontos]
    if tratamento == "tratado":
        valores = suavizar(valores)
    analise.registrar_resultado(valores, detector.detectar(valores, delta))  # Adapter em uso

    RepositorioDeAnalises().inserir(analise, valores)
    publicador_de_analise.notificar("analise_concluida", {  # Observer em uso
        "processo_id": processo_id,
        "mensagem": f"Análise “{analise.nome}” concluída: {len(analise.drifts)} desvio(s) encontrado(s).",
    })
    return ir_para(f"/analises/{analise.id}")


# ---- Read: detalhe com gráfico e desvios (o técnico também vê, sem editar)
@rotas.get("/analises/{id}", dependencies=[Depends(exigir("ver_analise"))])
def ver(request: Request, id: str):
    repo = RepositorioDeAnalises()
    analise = repo.obter_ou_erro(id)
    processo = RepositorioDeProcessos().obter(analise.processo_id)
    manutencoes = RepositorioDeManutencoes().listar_resumo(analise_id=id)
    return tela(request, "analises/detalhe.html", analise=analise, processo=processo, manutencoes=manutencoes,
                grafico=desenhar_grafico(repo.serie(id), [d.inicio_anomalia for d in analise.drifts]))


# ---- Update: renomear
@rotas.post("/analises/{id}/renomear", dependencies=so_gestor)
def renomear(id: str, nome: str = Form("")):
    repo = RepositorioDeAnalises()
    analise = repo.obter_ou_erro(id)
    analise.renomear(nome)
    repo.renomear(analise)
    return ir_para(f"/analises/{id}")


# ---- Delete
@rotas.post("/analises/{id}/excluir", dependencies=so_gestor)
def excluir(id: str):
    repo = RepositorioDeAnalises()
    analise = repo.obter_ou_erro(id)
    repo.excluir(id)
    return ir_para(f"/processos/{analise.processo_id}")


def desenhar_grafico(valores: list[float], inicios: list[int], largura=900, altura=240) -> dict:
    """Coordenadas do gráfico em SVG: a linha da série e uma marca em cada desvio."""
    if not valores:
        return {"linha": "", "marcas": [], "largura": largura, "altura": altura}
    menor, maior = min(valores), max(valores)
    escala = (maior - menor) or 1
    x = lambda i: round(i * largura / max(len(valores) - 1, 1), 1)  # noqa: E731
    y = lambda v: round(altura - 10 - (v - menor) * (altura - 20) / escala, 1)  # noqa: E731
    return {
        "linha": " ".join(f"{x(i)},{y(v)}" for i, v in enumerate(valores)),
        "marcas": [{"x": x(i), "numero": n} for n, i in enumerate(inicios, start=1)],
        "largura": largura,
        "altura": altura,
        "menor": round(menor, 1),
        "maior": round(maior, 1),
    }
