"""Acesso ao banco do CRUD de Processo: tabelas processos, eventos e operacoes."""

from __future__ import annotations

from driftor.banco import BancoDeDados
from driftor.dominio import Evento, Operacao, Processo, Trace

CAMPOS = "id, nome, status, arquivo, formato, total_traces, total_eventos, criado_em"


def _para_processo(linha: dict) -> Processo:
    return Processo(**{**linha, "id": str(linha["id"])})


class RepositorioDeProcessos:
    def __init__(self) -> None:
        self.banco = BancoDeDados()

    # ---- Read
    def listar(self) -> list[Processo]:
        linhas = self.banco.consultar(f"select {CAMPOS} from processos order by atualizado_em desc")
        return [_para_processo(linha) for linha in linhas]

    def obter(self, id: str) -> Processo | None:
        linha = self.banco.consultar_um(f"select {CAMPOS} from processos where id = :id", id=id)
        return _para_processo(linha) if linha else None

    # ---- Create
    def inserir(self, processo: Processo) -> None:
        self.banco.executar(
            "insert into processos (id, nome) values (:id, :nome)", id=processo.id, nome=processo.nome
        )

    # ---- Update
    def atualizar(self, processo: Processo) -> None:
        self.banco.executar(
            """update processos set nome = :nome, status = :status, arquivo = :arquivo, formato = :formato,
                   total_traces = :total_traces, total_eventos = :total_eventos, atualizado_em = now()
               where id = :id""",
            id=processo.id, nome=processo.nome, status=processo.status, arquivo=processo.arquivo,
            formato=processo.formato, total_traces=processo.total_traces, total_eventos=processo.total_eventos,
        )

    # ---- Delete (eventos, operações e análises caem junto: on delete cascade)
    def excluir(self, id: str) -> None:
        self.banco.executar("delete from processos where id = :id", id=id)

    # ---- Log de eventos
    def substituir_log(self, processo: Processo, traces: list[Trace], operacoes: list[Operacao]) -> None:
        self.banco.executar("delete from eventos where processo_id = :id", id=processo.id)
        self.banco.executar("delete from operacoes where processo_id = :id", id=processo.id)
        self.banco.executar_varios(
            """insert into eventos (processo_id, case_id, ordem, rotulo, inicio, duracao_s)
               values (:processo_id, :case_id, :ordem, :rotulo, :inicio, :duracao_s)""",
            [
                {"processo_id": processo.id, "case_id": t.case_id, "ordem": i,
                 "rotulo": e.rotulo, "inicio": e.inicio, "duracao_s": e.duracao_s}
                for t in traces for i, e in enumerate(t.eventos)
            ],
        )
        self.banco.executar_varios(
            """insert into operacoes (processo_id, rotulo, ocorrencias, casos)
               values (:processo_id, :rotulo, :ocorrencias, :casos)""",
            [{"processo_id": processo.id, "rotulo": o.rotulo, "ocorrencias": o.ocorrencias, "casos": o.casos}
             for o in operacoes],
        )
        self.atualizar(processo)

    def operacoes(self, processo_id: str) -> list[Operacao]:
        linhas = self.banco.consultar(
            """select o.rotulo, o.ocorrencias, o.casos, a.nome as atividade
               from operacoes o left join atividades a on a.id = o.atividade_id
               where o.processo_id = :id order by o.ocorrencias desc, o.rotulo""",
            id=processo_id,
        )
        return [Operacao(**linha) for linha in linhas]

    def salvar_mapeamento(self, processo_id: str, ligacoes: dict[str, str]) -> None:
        """ligacoes: rótulo do log -> id da atividade."""
        for rotulo, atividade_id in ligacoes.items():
            self.banco.executar(
                "update operacoes set atividade_id = :atividade_id where processo_id = :processo_id and rotulo = :rotulo",
                atividade_id=atividade_id, processo_id=processo_id, rotulo=rotulo,
            )

    def traces(self, processo_id: str) -> list[Trace]:
        """Remonta os traces a partir da tabela eventos, já com a atividade mapeada."""
        linhas = self.banco.consultar(
            """select e.case_id, e.rotulo, e.inicio, e.duracao_s, a.nome as atividade
               from eventos e
               left join operacoes o on o.processo_id = e.processo_id and o.rotulo = e.rotulo
               left join atividades a on a.id = o.atividade_id
               where e.processo_id = :id order by e.case_id, e.ordem""",
            id=processo_id,
        )
        por_caso: dict[str, Trace] = {}
        for linha in linhas:
            trace = por_caso.setdefault(linha["case_id"], Trace(case_id=linha["case_id"]))
            trace.eventos.append(Evento(linha["rotulo"], linha["inicio"], linha["duracao_s"], linha["atividade"]))
        return list(por_caso.values())
