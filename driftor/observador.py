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
    """Guarda o aviso que aparece no topo da próxima tela de um papel (gestor ou técnico).

    Cada caixa só aceita os eventos que interessam ao seu papel.
    """

    def __init__(self, eventos: set[str]) -> None:
        self.eventos = eventos
        self._mensagens: deque[str] = deque(maxlen=5)

    def atualizar(self, evento: str, dados: dict) -> None:
        if evento in self.eventos:
            self._mensagens.append(dados["mensagem"])

    def retirar_mensagens(self) -> list[str]:
        mensagens = list(self._mensagens)
        self._mensagens.clear()
        return mensagens


avisos_por_papel = {
    "gestor": AvisoNaTela({"analise_concluida", "manutencao_concluida"}),
    "tecnico": AvisoNaTela({"manutencao_disparada"}),
}
