"""O que todas as telas usam: templates, papel do usuário, redirecionamento e a trava de permissão."""

from __future__ import annotations

from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from driftor.config import PAPEIS, Configuracao
from driftor.observador import avisos_por_papel

templates = Jinja2Templates(directory=Path(__file__).with_name("templates"))
templates.env.filters["data"] = lambda d: d.astimezone(ZoneInfo("America/Sao_Paulo")).strftime("%d/%m/%Y %H:%M") if d else ""


class PrecisaEntrar(Exception):
    """Ninguém escolheu um perfil ainda: vai para a tela de entrada."""


class SemPermissao(Exception):
    """VARIABILIDADE: o papel de quem entrou não tem acesso a esta tela."""


def papel_atual(request: Request) -> str | None:
    papel = request.cookies.get("papel")
    return papel if papel in PAPEIS else None


def tela(request: Request, template: str, **dados):
    """Renderiza um template com a configuração, o papel e os avisos do Observer para este papel."""
    papel = papel_atual(request)
    avisos = avisos_por_papel[papel].retirar_mensagens() if papel else []
    return templates.TemplateResponse(
        request,
        template,
        {"config": Configuracao(), "papel": papel, "papeis": PAPEIS, "avisos": avisos, **dados},
    )


def ir_para(url: str) -> RedirectResponse:
    """Depois de um POST, volta para uma tela (padrão Post/Redirect/Get)."""
    return RedirectResponse(url, status_code=303)


def exigir(permissao: str):
    """VARIABILIDADE: a rota só abre se o papel de quem entrou tem a permissão."""

    def verificar(request: Request) -> str:
        papel = papel_atual(request)
        if papel is None:
            raise PrecisaEntrar()
        if not Configuracao().pode(papel, permissao):
            raise SemPermissao(permissao)
        return papel

    return verificar
