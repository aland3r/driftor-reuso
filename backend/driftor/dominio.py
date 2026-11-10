"""As principais classes do Driftor, com atributos e métodos.

Aqui ficam só as regras do negócio: nenhuma classe sabe de banco, tela ou biblioteca.
São 13 classes: Processo, Evento, Trace, Atividade, Operacao, Variante, No,
Aresta, Grafo, PontoDaSerie, Analise, Drift e Manutencao.
"""

from __future__ import annotations

import statistics
import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime


class ErroDeNegocio(ValueError):
    """Erro que o usuário consegue corrigir (vira mensagem na tela)."""


def novo_id() -> str:
    return str(uuid.uuid4())


def limpar_nome(nome: str | None) -> str:
    """Tira espaços sobrando: '  Torno   02 ' vira 'Torno 02'."""
    return " ".join((nome or "").split())


# ---------------------------------------------------------------- Processo ---

@dataclass
class Processo:
    id: str
    nome: str
    status: str = "vazio"          # vazio -> mapeando -> pronto
    arquivo: str | None = None
    formato: str | None = None
    total_traces: int = 0
    total_eventos: int = 0
    criado_em: datetime | None = None

    @staticmethod
    def criar(nome: str) -> Processo:
        nome = limpar_nome(nome)
        if not nome:
            raise ErroDeNegocio("Dê um nome ao processo.")
        return Processo(id=novo_id(), nome=nome)

    def renomear(self, novo_nome: str) -> None:
        novo_nome = limpar_nome(novo_nome)
        if not novo_nome:
            raise ErroDeNegocio("O nome não pode ficar vazio.")
        self.nome = novo_nome

    def carregar_log(self, arquivo: str, formato: str, traces: list[Trace]) -> None:
        """Um log novo substitui o anterior e o processo volta a precisar de mapeamento."""
        if not traces:
            raise ErroDeNegocio("O log não tem nenhum trace.")
        self.arquivo = arquivo
        self.formato = formato
        self.total_traces = len(traces)
        self.total_eventos = sum(len(t.eventos) for t in traces)
        self.status = "mapeando"

    def marcar_pronto(self) -> None:
        self.status = "pronto"

    def pode_analisar(self) -> bool:
        return self.status == "pronto"


# ------------------------------------------------------- Log de eventos ---

@dataclass
class Evento:
    rotulo: str                    # nome da operação como veio no log
    inicio: datetime | None
    duracao_s: float | None
    atividade: str | None = None   # preenchida depois do mapeamento

    def nome_no_grafo(self) -> str:
        return self.atividade or self.rotulo


@dataclass
class Trace:
    case_id: str
    eventos: list[Evento] = field(default_factory=list)

    def inicio(self) -> datetime | None:
        datas = [e.inicio for e in self.eventos if e.inicio]
        return min(datas) if datas else None

    def sequencia(self) -> tuple[str, ...]:
        return tuple(e.nome_no_grafo() for e in self.eventos)

    def duracao(self, atividades: set[str] | None = None) -> float | None:
        """Soma das durações (de todas as atividades ou só das escolhidas)."""
        valores = [
            e.duracao_s for e in self.eventos
            if e.duracao_s is not None and (not atividades or e.nome_no_grafo() in atividades)
        ]
        return float(sum(valores)) if valores else None


# ------------------------------------------------------------ Atividade ---

@dataclass
class Atividade:
    id: str
    nome: str
    descricao: str = ""

    @staticmethod
    def criar(nome: str, descricao: str = "") -> Atividade:
        nome = limpar_nome(nome)
        if not nome:
            raise ErroDeNegocio("Dê um nome à atividade.")
        return Atividade(id=novo_id(), nome=nome, descricao=(descricao or "").strip())

    def editar(self, nome: str, descricao: str) -> None:
        nome = limpar_nome(nome)
        if not nome:
            raise ErroDeNegocio("O nome não pode ficar vazio.")
        self.nome = nome
        self.descricao = (descricao or "").strip()


@dataclass
class Operacao:
    """Um rótulo do log ligado (ou ainda não) a uma atividade do catálogo."""

    rotulo: str
    ocorrencias: int
    casos: int
    atividade: str | None = None

    @staticmethod
    def contar(traces: list[Trace]) -> list[Operacao]:
        """Uma operação por rótulo do log, da mais frequente para a menos frequente."""
        ocorrencias: Counter[str] = Counter()
        casos: dict[str, set[str]] = defaultdict(set)
        for trace in traces:
            for evento in trace.eventos:
                ocorrencias[evento.rotulo] += 1
                casos[evento.rotulo].add(trace.case_id)
        return [
            Operacao(rotulo=r, ocorrencias=n, casos=len(casos[r]))
            for r, n in sorted(ocorrencias.items(), key=lambda item: (-item[1], item[0]))
        ]

    def sugerir_atividade(self, catalogo: list[Atividade]) -> str:
        """Atividade do catálogo com o mesmo nome; se não houver, o próprio rótulo."""
        for atividade in catalogo:
            if atividade.nome.casefold() == limpar_nome(self.rotulo).casefold():
                return atividade.nome
        return limpar_nome(self.rotulo)

    def mapear(self, atividade: str) -> None:
        atividade = limpar_nome(atividade)
        if not atividade:
            raise ErroDeNegocio(f"Escolha uma atividade para a operação {self.rotulo}.")
        self.atividade = atividade


# ---------------------------------------------------------------- Grafo ---

@dataclass
class Variante:
    numero: int
    sequencia: tuple[str, ...]
    total_traces: int
    participacao: float

    @staticmethod
    def agrupar(traces: list[Trace]) -> list[Variante]:
        """Traces com a mesma sequência de atividades formam uma variante."""
        contagem = Counter(t.sequencia() for t in traces)
        total = len(traces) or 1
        ordenadas = sorted(contagem.items(), key=lambda item: (-item[1], item[0]))
        return [
            Variante(numero=i, sequencia=seq, total_traces=n, participacao=n / total)
            for i, (seq, n) in enumerate(ordenadas, start=1)
        ]

    def descricao(self) -> str:
        return " → ".join(self.sequencia)


@dataclass
class No:
    atividade: str
    frequencia: int
    duracao_media_s: float

    def rotulo(self) -> str:
        return f"{self.atividade} ({self.frequencia})"


@dataclass
class Aresta:
    origem: str
    destino: str
    frequencia: int


@dataclass
class Grafo:
    nos: list[No]
    arestas: list[Aresta]

    @staticmethod
    def montar(traces: list[Trace], arestas: list[Aresta]) -> Grafo:
        """Junta a frequência de cada atividade às arestas que o minerador descobriu."""
        frequencia: Counter[str] = Counter()
        duracoes: dict[str, list[float]] = defaultdict(list)
        for trace in traces:
            for evento in trace.eventos:
                frequencia[evento.nome_no_grafo()] += 1
                if evento.duracao_s is not None:
                    duracoes[evento.nome_no_grafo()].append(evento.duracao_s)
        nos = [
            No(a, n, round(statistics.fmean(duracoes[a]), 1) if duracoes[a] else 0.0)
            for a, n in frequencia.most_common()
        ]
        return Grafo(nos=nos, arestas=sorted(arestas, key=lambda a: -a.frequencia))

    def para_mermaid(self) -> str:
        """Texto do diagrama que a tela desenha com o Mermaid."""
        ids = {no.atividade: f"n{i}" for i, no in enumerate(self.nos)}
        linhas = ["flowchart LR"]
        linhas += [f'    {ids[no.atividade]}["{no.rotulo()}"]' for no in self.nos]
        linhas += [
            f"    {ids[a.origem]} -->|{a.frequencia}| {ids[a.destino]}"
            for a in self.arestas if a.origem in ids and a.destino in ids
        ]
        return "\n".join(linhas)


# -------------------------------------------------------------- Análise ---

@dataclass
class PontoDaSerie:
    posicao: int
    case_id: str
    valor: float

    @staticmethod
    def serie_de_duracao(traces: list[Trace], atividade: str | None) -> list[PontoDaSerie]:
        """Uma observação por trace, em ordem de início: é o que vai para o ADWIN."""
        filtro = {atividade} if atividade else None
        ordenados = sorted(traces, key=lambda t: (t.inicio() is None, t.inicio() or datetime.min))
        pontos: list[PontoDaSerie] = []
        for trace in ordenados:
            valor = trace.duracao(filtro)
            if valor is not None:
                pontos.append(PontoDaSerie(len(pontos), trace.case_id, valor))
        return pontos


@dataclass
class Drift:
    id: str
    posicao: int
    indice: int
    inicio_anomalia: int
    media_antes: float
    media_depois: float
    variacao_pct: float

    def aumentou(self) -> bool:
        return self.media_depois > self.media_antes

    def resumo(self) -> str:
        sentido = "subiu" if self.aumentou() else "caiu"
        return f"A duração {sentido} {abs(self.variacao_pct):.1f}% a partir do trace {self.inicio_anomalia}."


@dataclass
class Analise:
    id: str
    processo_id: str
    nome: str
    delta: float
    tratamento: str                # bruto | tratado
    atividade: str | None = None
    total_observacoes: int = 0
    drifts: list[Drift] = field(default_factory=list)

    @staticmethod
    def criar(processo: Processo, nome: str, delta: float, tratamento: str, atividade: str | None) -> Analise:
        if not processo.pode_analisar():
            raise ErroDeNegocio("Mapeie as operações do processo antes de analisar.")
        if not 0 < delta < 1:
            raise ErroDeNegocio("δ precisa estar entre 0 e 1.")
        if tratamento not in ("bruto", "tratado"):
            raise ErroDeNegocio("Tratamento deve ser 'bruto' ou 'tratado'.")
        atividade = limpar_nome(atividade) or None
        nome = limpar_nome(nome) or f"{processo.nome} · {atividade or 'trace inteiro'}"
        return Analise(novo_id(), processo.id, nome, delta, tratamento, atividade)

    def renomear(self, novo_nome: str) -> None:
        novo_nome = limpar_nome(novo_nome)
        if not novo_nome:
            raise ErroDeNegocio("O nome não pode ficar vazio.")
        self.nome = novo_nome

    def registrar_resultado(self, valores: list[float], inicios: list[tuple[int, int]]) -> None:
        """Recebe (índice da detecção, início da anomalia) de cada desvio e calcula as médias."""
        self.total_observacoes = len(valores)
        limites = [0, *[inicio for _, inicio in inicios], len(valores)]
        self.drifts = []
        for posicao, (indice, inicio) in enumerate(inicios, start=1):
            antes = valores[limites[posicao - 1]:inicio] or valores[:1]
            depois = valores[inicio:limites[posicao + 1]] or valores[-1:]
            media_antes, media_depois = statistics.fmean(antes), statistics.fmean(depois)
            variacao = (media_depois - media_antes) / abs(media_antes) * 100 if media_antes else 0.0
            self.drifts.append(
                Drift(novo_id(), posicao, indice, inicio, round(media_antes, 3), round(media_depois, 3), round(variacao, 2))
            )


@dataclass
class Manutencao:
    """Ordem de manutenção que o gestor dispara a partir de um desvio e o técnico conclui."""

    id: str
    analise_id: str
    drift_id: str | None
    descricao: str
    status: str = "pendente"       # pendente -> concluida
    observacoes: str = ""
    criado_em: datetime | None = None
    concluida_em: datetime | None = None

    @staticmethod
    def disparar(analise: Analise, drift_id: str | None, descricao: str) -> Manutencao:
        if drift_id and drift_id not in {d.id for d in analise.drifts}:
            raise ErroDeNegocio("Este desvio não pertence à análise.")
        descricao = (descricao or "").strip()
        if not descricao:
            raise ErroDeNegocio("Descreva o que o técnico deve verificar.")
        return Manutencao(novo_id(), analise.id, drift_id or None, descricao)

    def esta_pendente(self) -> bool:
        return self.status == "pendente"

    def editar(self, descricao: str) -> None:
        if not self.esta_pendente():
            raise ErroDeNegocio("Uma manutenção concluída não pode mais ser alterada.")
        descricao = (descricao or "").strip()
        if not descricao:
            raise ErroDeNegocio("A descrição não pode ficar vazia.")
        self.descricao = descricao

    def concluir(self, observacoes: str) -> None:
        if not self.esta_pendente():
            raise ErroDeNegocio("Esta manutenção já foi concluída.")
        observacoes = (observacoes or "").strip()
        if not observacoes:
            raise ErroDeNegocio("Escreva as observações do que foi feito.")
        self.status = "concluida"
        self.observacoes = observacoes
