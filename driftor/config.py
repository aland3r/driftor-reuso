"""PADRÃO SINGLETON, exemplo 1: Configuracao.

Lê as variáveis de ambiente e as regras de papel uma única vez. Qualquer parte
do código que fizer Configuracao() recebe o MESMO objeto, então todas as telas
seguem as mesmas regras de acesso e usam o mesmo endereço do banco.
"""

from __future__ import annotations

import os

# VARIABILIDADE por papel: o que cada perfil vê e pode fazer no mesmo produto.
PAPEIS = {
    "gestor": {
        "nome": "Gestor",
        "descricao": "Mapeia os processos, gera as análises de desvio e dispara as manutenções.",
        "inicio": "/processos",
        "pode": {"processos", "atividades", "analises", "ver_analise", "manutencoes", "disparar_manutencao"},
    },
    "tecnico": {
        "nome": "Técnico de manutenção",
        "descricao": "Recebe as manutenções disparadas, executa e registra as observações.",
        "inicio": "/manutencoes",
        "pode": {"manutencoes", "ver_analise", "concluir_manutencao"},
    },
}


class Configuracao:
    _instancia: Configuracao | None = None

    def __new__(cls) -> Configuracao:
        # Só cria o objeto na primeira chamada; nas outras devolve o mesmo.
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._carregar()
        return cls._instancia

    def _carregar(self) -> None:
        self.url_do_banco = os.environ.get(
            "DATABASE_URL", "postgresql://driftor_reuso:local@localhost:5432/driftor"
        )
        self.papeis = PAPEIS

    def pode(self, papel: str | None, permissao: str) -> bool:
        """Pergunta da variabilidade: este papel tem esta permissão?"""
        return papel in self.papeis and permissao in self.papeis[papel]["pode"]

    def nome_do_papel(self, papel: str) -> str:
        return self.papeis[papel]["nome"]
