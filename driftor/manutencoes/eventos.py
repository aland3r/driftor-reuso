"""PADRÃO OBSERVER, exemplo 2: manutenção disparada e manutenção concluída.

Sujeito: publicador_de_manutencao. Observadores: a caixa de avisos do técnico
(recebe "manutencao_disparada") e a do gestor (recebe "manutencao_concluida"),
as duas em driftor/observador.py. As inscrições ficam em driftor/main.py.
"""

from __future__ import annotations

from driftor.observador import Sujeito

publicador_de_manutencao = Sujeito()
