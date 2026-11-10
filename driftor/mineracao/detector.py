"""PADRÃO ADAPTER, exemplo 2: o ADWIN da biblioteca river adaptado à interface DetectorDeDrift.

O app só conhece DetectorDeDrift.detectar(valores, delta), que devolve a lista de
desvios como (índice da detecção, início da anomalia). O ADWIN do river é
incremental: recebe um valor por vez em update() e liga a flag drift_detected.
O adaptador percorre a série, observa a flag e monta a resposta no formato do app.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from river.drift import ADWIN


class DetectorDeDrift(ABC):
    """Interface que o app espera (o "alvo" do Adapter)."""

    @abstractmethod
    def detectar(self, valores: list[float], delta: float) -> list[tuple[int, int]]: ...


class RiverAdwinAdapter(DetectorDeDrift):
    """Adaptador: implementa a interface do app usando o ADWIN do river por dentro."""

    def detectar(self, valores: list[float], delta: float) -> list[tuple[int, int]]:
        adwin = ADWIN(delta=delta)  # biblioteca adaptada (o "adaptado")
        desvios: list[tuple[int, int]] = []
        inicio_do_trecho = 0
        for indice, valor in enumerate(valores):
            adwin.update(valor)
            if adwin.drift_detected:
                inicio = estimar_inicio(valores, indice, int(adwin.width), inicio_do_trecho)
                desvios.append((indice, inicio))
                inicio_do_trecho = indice + 1
        return desvios


def estimar_inicio(valores: list[float], deteccao: int, largura: int, inicio_do_trecho: int) -> int:
    """O ADWIN avisa com atraso; procura o ponto que melhor separa os dois níveis antes do aviso.

    Mesma regra da pesquisa IPDD/ADWIN (reaproveitada da Function fn-adwin).
    """
    janela = max(largura * 4, 64)
    comeco = max(inicio_do_trecho, deteccao - janela + 1)
    amostra = valores[comeco:deteccao + 1]
    minimo = min(5, max(2, len(amostra) // 4))
    if len(amostra) < minimo * 2:
        return max(inicio_do_trecho, deteccao - largura + 1)

    soma, quadrados = [0.0], [0.0]
    for valor in amostra:
        soma.append(soma[-1] + valor)
        quadrados.append(quadrados[-1] + valor * valor)

    def erro(esq: int, dir: int) -> float:
        n = dir - esq
        total = soma[dir] - soma[esq]
        return max(0.0, quadrados[dir] - quadrados[esq] - total * total / n)

    corte = min(range(minimo, len(amostra) - minimo + 1), key=lambda p: erro(0, p) + erro(p, len(amostra)))
    return comeco + corte


def suavizar(valores: list[float]) -> list[float]:
    """Tratamento 'tratado': média móvel centrada, janela min(15, max(3, n // 20))."""
    janela = min(15, max(3, len(valores) // 20))
    esquerda, direita = (janela - 1) // 2, janela // 2
    return [
        sum(trecho) / len(trecho)
        for i in range(len(valores))
        for trecho in [valores[max(0, i - esquerda):min(len(valores), i + direita + 1)]]
    ]
