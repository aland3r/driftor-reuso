"""PADRÃO OBSERVER: a base usada pelos dois exemplos.

Sujeito guarda uma lista de observadores e avisa todos quando algo acontece.
Quem publica o evento não conhece quem reage a ele: basta inscrever um
observador novo para acrescentar uma reação, sem mexer no publicador.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque


class Observador(ABC):
    @abstractmethod
    def atualizar(self, evento: str, dados: dict) -> None: ...


class Sujeito:
    def __init__(self) -> None:
        self._observadores: list[Observador] = []

    def inscrever(self, observador: Observador) -> None:
        if observador not in self._observadores:
            self._observadores.append(observador)

    def cancelar(self, observador: Observador) -> None:
        self._observadores.remove(observador)

    def notificar(self, evento: str, dados: dict) -> None:
        for observador in self._observadores:
            observador.atualizar(evento, dados)


class AvisoNaTela(Observador):
    """Observador comum aos dois exemplos: guarda a mensagem que aparece no topo da próxima tela."""

    def __init__(self) -> None:
        self._mensagens: deque[str] = deque(maxlen=5)

    def atualizar(self, evento: str, dados: dict) -> None:
        self._mensagens.append(dados["mensagem"])

    def retirar_mensagens(self) -> list[str]:
        mensagens = list(self._mensagens)
        self._mensagens.clear()
        return mensagens


aviso_na_tela = AvisoNaTela()
