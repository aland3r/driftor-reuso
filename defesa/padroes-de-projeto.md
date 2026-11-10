# Os três padrões de projeto (Opção 02: 3 padrões, 2 exemplos de cada)

Os dois integrantes precisam saber este arquivo inteiro. Para cada padrão: primeiro a ideia em poucas linhas, depois o desenho com as classes reais e, por fim, o código. Os links apontam para o commit `48c729e`.

| Padrão | Família | Exemplo 1 | Exemplo 2 |
|---|---|---|---|
| Singleton | criacional | `Configuracao` | `BancoDeDados` |
| Adapter | estrutural | `Pm4pyMineradorAdapter` | `RiverAdwinAdapter` |
| Observer | comportamental | análise concluída | nota criada ou excluída |

## 1. Singleton

**A ideia.** A classe garante que existe **um único objeto** dela no programa inteiro e dá um ponto de acesso a ele. Quem chama `Classe()` pela segunda vez recebe o mesmo objeto da primeira vez.

**Como foi feito.** O atributo de classe `_instancia` guarda o objeto. O método `__new__` (que o Python chama antes de criar qualquer objeto) só cria um objeto novo quando `_instancia` está vazio.

```mermaid
classDiagram
    class Configuracao {
        -_instancia: Configuracao
        +url_do_banco: str
        +edicao: str
        +__new__() Configuracao
        +tem_recurso(recurso) bool
        +nome_da_edicao() str
    }
    class BancoDeDados {
        -_instancia: BancoDeDados
        +engine: Engine
        +__new__() BancoDeDados
        +consultar(sql) list
        +executar(sql) int
        +aplicar_schema()
    }
    BancoDeDados ..> Configuracao : lê url_do_banco
```

### 1.1 Exemplo 1: `Configuracao`

Lê as variáveis de ambiente uma vez só. Por isso todas as telas enxergam a mesma edição do produto.

📍 `driftor/config.py` · linhas 19–27 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/48c729e/driftor/config.py#L19-L27)

```python
class Configuracao:
    _instancia: Configuracao | None = None

    def __new__(cls) -> Configuracao:
        # Só cria o objeto na primeira chamada; nas outras devolve o mesmo.
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._carregar()
        return cls._instancia
```

### 1.2 Exemplo 2: `BancoDeDados`

Abre uma conexão (pool) para o app inteiro. Todos os repositórios recebem o mesmo objeto.

📍 `driftor/banco.py` · linhas 20–28 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/48c729e/driftor/banco.py#L20-L28)

```python
class BancoDeDados:
    _instancia: BancoDeDados | None = None

    def __new__(cls) -> BancoDeDados:
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            url = Configuracao().url_do_banco.replace("postgresql://", "postgresql+psycopg://", 1)
            cls._instancia.engine: Engine = create_engine(url, pool_pre_ping=True)
        return cls._instancia
```

**Prova:** o teste `test_singletons_devolvem_o_mesmo_objeto`, em `tests/test_cruds.py`, confere que `Configuracao() is Configuracao()` e `BancoDeDados() is BancoDeDados()`.

## 2. Adapter

**A ideia.** Faz uma classe com uma interface incompatível funcionar onde o programa espera outra interface. É como o adaptador de tomada: o programa (cliente) só conhece a **interface alvo**; o **adaptador** implementa essa interface e, por dentro, chama a biblioteca (**adaptado**) traduzindo a entrada e a saída.

```mermaid
classDiagram
    class MineradorDeGrafo {
        <<interface>>
        +descobrir_arestas(traces) list~Aresta~
    }
    class Pm4pyMineradorAdapter {
        +descobrir_arestas(traces) list~Aresta~
    }
    class pm4py {
        <<biblioteca>>
        +discover_dfg(DataFrame) dict
    }
    MineradorDeGrafo <|.. Pm4pyMineradorAdapter
    Pm4pyMineradorAdapter ..> pm4py : traduz e chama

    class DetectorDeDrift {
        <<interface>>
        +detectar(valores, delta) list
    }
    class RiverAdwinAdapter {
        +detectar(valores, delta) list
    }
    class ADWIN {
        <<biblioteca river>>
        +update(valor)
        +drift_detected: bool
    }
    DetectorDeDrift <|.. RiverAdwinAdapter
    RiverAdwinAdapter ..> ADWIN : traduz e chama
```

### 2.1 Exemplo 1: o PM4Py vira um `MineradorDeGrafo`

O PM4Py quer uma tabela do pandas e devolve um dicionário `{(origem, destino): frequência}`. O app quer passar `Trace` e receber `Aresta`.

📍 `driftor/mineracao/grafo.py` · linhas 18–48 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/48c729e/driftor/mineracao/grafo.py#L18-L48)

```python
class MineradorDeGrafo(ABC):
    """Interface que o app espera (o "alvo" do Adapter)."""

    @abstractmethod
    def descobrir_arestas(self, traces: list[Trace]) -> list[Aresta]: ...


class Pm4pyMineradorAdapter(MineradorDeGrafo):
    """Adaptador: implementa a interface do app usando o PM4Py por dentro."""

    def descobrir_arestas(self, traces: list[Trace]) -> list[Aresta]:
        import pm4py  # biblioteca adaptada (o "adaptado")

        # 1. Traduz Traces do domínio para a tabela que o PM4Py entende.
        linhas = [
            {
                "case_id": trace.case_id,
                "atividade": evento.nome_no_grafo(),
                "momento": pd.Timestamp("2000-01-01", tz="UTC") + pd.Timedelta(seconds=posicao),
            }
            for trace in traces
            for posicao, evento in enumerate(trace.eventos)
        ]
        if not linhas:
            return []
        # 2. Chama o PM4Py: grafo de sequência direta (DFG).
        dfg, _inicios, _fins = pm4py.discover_dfg(
            pd.DataFrame(linhas), case_id_key="case_id", activity_key="atividade", timestamp_key="momento"
        )
        # 3. Traduz a resposta do PM4Py de volta para Arestas do domínio.
        return [Aresta(origem=o, destino=d, frequencia=int(n)) for (o, d), n in dfg.items()]
```

Onde o cliente usa (só conhece a interface):

📍 `driftor/processos/rotas.py` · linhas 47–47 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/48c729e/driftor/processos/rotas.py#L47-L47)

```python
        grafo = Grafo.montar(traces, minerador.descobrir_arestas(traces))  # Adapter em uso
```

### 2.2 Exemplo 2: o ADWIN do river vira um `DetectorDeDrift`

O ADWIN recebe um valor por vez em `update()` e liga a flag `drift_detected`. O app quer passar a série inteira e receber a lista de desvios.

📍 `driftor/mineracao/detector.py` · linhas 16–36 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/48c729e/driftor/mineracao/detector.py#L16-L36)

```python
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
```

Onde o cliente usa:

📍 `driftor/analises/rotas.py` · linhas 47–47 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/48c729e/driftor/analises/rotas.py#L47-L47)

```python
    analise.registrar_resultado(valores, detector.detectar(valores, delta))  # Adapter em uso
```

**Por que é reuso.** Trocar o PM4Py ou o river por outra biblioteca exige mudar só o adaptador. Rotas, domínio e telas continuam iguais.

## 3. Observer

**A ideia.** Um objeto (o **sujeito**) mantém uma lista de **observadores** e avisa todos quando algo acontece. O sujeito não sabe o que cada observador faz. Para acrescentar uma reação nova, basta inscrever mais um observador, sem mexer em quem publica.

```mermaid
classDiagram
    class Sujeito {
        -_observadores: list
        +inscrever(observador)
        +cancelar(observador)
        +notificar(evento, dados)
    }
    class Observador {
        <<abstract>>
        +atualizar(evento, dados)
    }
    class AtualizadorDoProcesso
    class ContadorDeNotas
    class AvisoNaTela {
        +retirar_mensagens() list
    }
    Sujeito o--> Observador : avisa todos
    Observador <|-- AtualizadorDoProcesso
    Observador <|-- ContadorDeNotas
    Observador <|-- AvisoNaTela
```

### 3.1 A base

📍 `driftor/observador.py` · linhas 14–32 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/48c729e/driftor/observador.py#L14-L32)

```python
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
```

### 3.2 As inscrições (quem observa o quê)

📍 `driftor/main.py` · linhas 33–37 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/48c729e/driftor/main.py#L33-L37)

```python
# OBSERVER: quem reage a cada evento é decidido aqui, não dentro de quem publica.
publicador_de_analise.inscrever(AtualizadorDoProcesso())
publicador_de_analise.inscrever(aviso_na_tela)
publicador_de_notas.inscrever(ContadorDeNotas())
publicador_de_notas.inscrever(aviso_na_tela)
```

### 3.3 Exemplo 1: análise concluída

Sujeito: `publicador_de_analise`. Observadores: `AtualizadorDoProcesso` (o processo sobe na lista) e `AvisoNaTela` (o aviso amarelo no topo).

📍 `driftor/analises/eventos.py` · linhas 12–22 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/48c729e/driftor/analises/eventos.py#L12-L22)

```python
publicador_de_analise = Sujeito()


class AtualizadorDoProcesso(Observador):
    """Marca o processo como recém-movimentado, para ele subir na lista de processos."""

    def atualizar(self, evento: str, dados: dict) -> None:
        if evento == "analise_concluida":
            BancoDeDados().executar(
                "update processos set atualizado_em = now() where id = :id", id=dados["processo_id"]
            )
```

Quem publica:

📍 `driftor/analises/rotas.py` · linhas 50–53 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/48c729e/driftor/analises/rotas.py#L50-L53)

```python
    publicador_de_analise.notificar("analise_concluida", {  # Observer em uso
        "processo_id": processo_id,
        "mensagem": f"Análise “{analise.nome}” concluída: {len(analise.drifts)} desvio(s) encontrado(s).",
    })
```

### 3.4 Exemplo 2: nota criada ou excluída

Sujeito: `publicador_de_notas`. Observadores: `ContadorDeNotas` (atualiza o total de notas da análise) e `AvisoNaTela`.

📍 `driftor/notas/eventos.py` · linhas 12–26 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/48c729e/driftor/notas/eventos.py#L12-L26)

```python
publicador_de_notas = Sujeito()


class ContadorDeNotas(Observador):
    """Mantém em dia o total de notas que aparece no cartão da análise."""

    def atualizar(self, evento: str, dados: dict) -> None:
        if evento in ("nota_criada", "nota_excluida"):
            BancoDeDados().executar(
                """update analises set total_notas = (
                       select count(*) from notas_drift n join drifts d on d.id = n.drift_id
                       where d.analise_id = :analise_id)
                   where id = :analise_id""",
                analise_id=dados["analise_id"],
            )
```

Quem publica:

📍 `driftor/notas/rotas.py` · linhas 37–37 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/48c729e/driftor/notas/rotas.py#L37-L37)

```python
    publicador_de_notas.notificar("nota_criada", {"analise_id": analise_id, "mensagem": "Nota salva."})  # Observer
```

**Na tela.** O aviso amarelo "Análise … concluída: 9 desvio(s) encontrado(s)." e o aviso "Nota salva." são o `AvisoNaTela` funcionando.

## 4. As 13 classes principais

Ficam em `driftor/dominio.py`, cada uma com atributos e métodos:

| Classe | Atributos principais | Métodos |
|---|---|---|
| `Processo` | nome, status, arquivo, total_traces | `criar`, `renomear`, `carregar_log`, `marcar_pronto`, `pode_analisar` |
| `Evento` | rotulo, inicio, duracao_s, atividade | `nome_no_grafo` |
| `Trace` | case_id, eventos | `inicio`, `sequencia`, `duracao` |
| `Atividade` | nome, descricao | `criar`, `editar` |
| `Operacao` | rotulo, ocorrencias, casos, atividade | `contar`, `sugerir_atividade`, `mapear` |
| `Variante` | numero, sequencia, total_traces | `agrupar`, `descricao` |
| `No` | atividade, frequencia, duracao_media_s | `rotulo` |
| `Aresta` | origem, destino, frequencia | (dados) |
| `Grafo` | nos, arestas | `montar`, `para_mermaid` |
| `PontoDaSerie` | posicao, case_id, valor | `serie_de_duracao` |
| `Analise` | nome, delta, tratamento, drifts | `criar`, `renomear`, `registrar_resultado` |
| `Drift` | inicio_anomalia, media_antes, media_depois | `aumentou`, `resumo` |
| `NotaDeDrift` | drift_id, texto | `criar`, `editar` |

Além delas: `Configuracao`, `BancoDeDados`, os quatro repositórios, `RepositorioBase`, os dois adaptadores e as classes do Observer.
