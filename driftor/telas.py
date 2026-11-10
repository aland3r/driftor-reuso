"""O que todas as telas usam: os templates Jinja, o redirecionamento e a trava de recurso."""

from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from driftor.config import Configuracao
from driftor.observador import aviso_na_tela

templates = Jinja2Templates(directory=Path(__file__).with_name("templates"))


def tela(request: Request, template: str, **dados):
    """Renderiza um template já com a edição do produto e os avisos do Observer."""
    return templates.TemplateResponse(
        request,
        template,
        {"config": Configuracao(), "avisos": aviso_na_tela.retirar_mensagens(), **dados},
    )


def ir_para(url: str) -> RedirectResponse:
    """Depois de um POST, volta para uma tela (padrão Post/Redirect/Get)."""
    return RedirectResponse(url, status_code=303)


def exigir_recurso(recurso: str):
    """VARIABILIDADE: bloqueia as rotas de um recurso que a edição não tem."""

    def verificar() -> None:
        if not Configuracao().tem_recurso(recurso):
            raise HTTPException(404, f"A edição {Configuracao().nome_da_edicao()} não tem {recurso}.")

    return verificar
