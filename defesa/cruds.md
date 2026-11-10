# CRUDs

Links fixos no commit `420f1db`. Todo CRUD segue o mesmo caminho:

```
botão (formulário) → rota em rotas.py → classe de dominio.py (regra) → repositorio.py (SQL) → BancoDeDados → Postgres
```

Todos os caminhos abaixo ficam dentro de `backend/driftor/`.

| CRUD | Pasta | Classes | Tabelas |
|---|---|---|---|
| Processo | `processos/` | `Processo` | processos, eventos, operacoes |
| Atividade | `atividades/` | `Atividade` | atividades |
| Análise | `analises/` | `Analise`, `Drift` | analises, drifts |
| Manutenção | `manutencoes/` | `Manutencao` | manutencoes |

Em cada pasta: `rotas.py` recebe a requisição e `repositorio.py` tem o SQL. As classes ficam em `dominio.py`.

**O que vem de `RepositorioBase` (herdado por todos):** `listar`, `obter`, `obter_ou_erro` e `excluir`. Por isso alguns Read e Delete não têm SQL no repositório do próprio CRUD.

📍 `backend/driftor/repositorio_base.py` · linhas 30–47 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/repositorio_base.py#L30-L47)

```python
    # ---- Read
    def listar(self) -> list[T]:
        linhas = self.banco.consultar(f"select {self.colunas} from {self.tabela} order by {self.ordem}")
        return [self.criar_objeto(linha) for linha in linhas]

    def obter(self, id: str) -> T | None:
        linha = self.banco.consultar_um(f"select {self.colunas} from {self.tabela} where id = :id", id=id)
        return self.criar_objeto(linha) if linha else None

    def obter_ou_erro(self, id: str) -> T:
        objeto = self.obter(id)
        if objeto is None:
            raise ErroDeNegocio(f"{self.nome_no_singular.capitalize()} não encontrado(a).")
        return objeto

    # ---- Delete
    def excluir(self, id: str) -> None:
        self.banco.executar(f"delete from {self.tabela} where id = :id", id=id)
```

---

## 1. Processo

| Operação | Requisição | Rota → regra → SQL |
|---|---|---|
| Create | `POST /processos` | `criar` → `Processo.criar` → `inserir` → `insert into processos` |
| Read (lista) | `GET /processos` | `listar` → `listar` (base) |
| Read (detalhe) | `GET /processos/{id}` | `ver` → `Grafo.montar`, `Variante.agrupar` → `obter_ou_erro` (base), `traces` |
| Update (log) | `POST /processos/{id}/log` | `carregar_log` → `Processo.carregar_log` → `substituir_log` |
| Update (mapeamento) | `POST /processos/{id}/operacoes` | `salvar_operacoes` → `Operacao.mapear`, `Processo.marcar_pronto` → `salvar_mapeamento`, `atualizar` |
| Update (nome) | `POST /processos/{id}/renomear` | `renomear` → `Processo.renomear` → `atualizar` → `update processos` |
| Delete | `POST /processos/{id}/excluir` | `excluir` → `excluir` (base) → `delete from processos` |


### Create

📍 `backend/driftor/processos/rotas.py` · linhas 28–33 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/processos/rotas.py#L28-L33)

```python
# ---- Create: só o nome; o log vem depois, na página do processo
@rotas.post("/processos")
def criar(nome: str = Form("")):
    processo = Processo.criar(nome)
    RepositorioDeProcessos().inserir(processo)
    return ir_para(f"/processos/{processo.id}")
```

📍 `backend/driftor/processos/repositorio.py` · linhas 19–23 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/processos/repositorio.py#L19-L23)

```python
    # ---- Create
    def inserir(self, processo: Processo) -> None:
        self.banco.executar(
            "insert into processos (id, nome) values (:id, :nome)", id=processo.id, nome=processo.nome
        )
```

### Read

📍 `backend/driftor/processos/rotas.py` · linhas 22–25 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/processos/rotas.py#L22-L25)

```python
# ---- Read: lista de processos (tela inicial)
@rotas.get("/processos")
def listar(request: Request):
    return tela(request, "processos/lista.html", processos=RepositorioDeProcessos().listar())
```

📍 `backend/driftor/processos/rotas.py` · linhas 36–51 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/processos/rotas.py#L36-L51)

```python
# ---- Read: detalhe do processo (grafo, variantes e análises)
@rotas.get("/processos/{id}")
def ver(request: Request, id: str, minerador: MineradorDeGrafo = Depends(minerador)):
    repo = RepositorioDeProcessos()
    processo = repo.obter_ou_erro(id)
    if processo.status == "mapeando":
        return ir_para(f"/processos/{id}/operacoes")
    grafo, variantes, analises, atividades = None, [], [], []
    if processo.pode_analisar():
        traces = repo.traces(id)
        grafo = Grafo.montar(traces, minerador.descobrir_arestas(traces))  # Adapter em uso
        variantes = Variante.agrupar(traces)
        atividades = [no.atividade for no in grafo.nos]
        analises = RepositorioDeAnalises().listar_resumo(processo_id=id)
    return tela(request, "processos/detalhe.html", processo=processo, grafo=grafo,
                variantes=variantes, analises=analises, atividades=atividades)
```

### Update

📍 `backend/driftor/processos/rotas.py` · linhas 54–62 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/processos/rotas.py#L54-L62)

```python
# ---- Update: carregar o log de eventos no processo
@rotas.post("/processos/{id}/log")
async def carregar_log(id: str, arquivo: UploadFile = File(...)):
    repo = RepositorioDeProcessos()
    processo = repo.obter_ou_erro(id)
    formato, traces = ler_log(await arquivo.read(), arquivo.filename or "")
    processo.carregar_log(arquivo.filename or "", formato, traces)
    repo.substituir_log(processo, traces, Operacao.contar(traces))
    return ir_para(f"/processos/{id}/operacoes")
```

📍 `backend/driftor/processos/rotas.py` · linhas 77–94 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/processos/rotas.py#L77-L94)

```python
@rotas.post("/processos/{id}/operacoes")
async def salvar_operacoes(request: Request, id: str):
    repo = RepositorioDeProcessos()
    processo = repo.obter_ou_erro(id)
    formulario = await request.form()
    atividades = RepositorioDeAtividades()
    ligacoes: dict[str, str] = {}
    for operacao in repo.operacoes(id):
        operacao.mapear(str(formulario.get(f"op::{operacao.rotulo}", "")))
        atividade = atividades.obter_por_nome(operacao.atividade)
        if atividade is None:  # nome novo entra no catálogo
            atividade = Atividade.criar(operacao.atividade)
            atividades.inserir(atividade)
        ligacoes[operacao.rotulo] = atividade.id
    repo.salvar_mapeamento(id, ligacoes)
    processo.marcar_pronto()
    repo.atualizar(processo)
    return ir_para(f"/processos/{id}")
```

📍 `backend/driftor/processos/rotas.py` · linhas 97–104 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/processos/rotas.py#L97-L104)

```python
# ---- Update: renomear
@rotas.post("/processos/{id}/renomear")
def renomear(id: str, nome: str = Form("")):
    repo = RepositorioDeProcessos()
    processo = repo.obter_ou_erro(id)
    processo.renomear(nome)
    repo.atualizar(processo)
    return ir_para(f"/processos/{id}")
```

📍 `backend/driftor/processos/repositorio.py` · linhas 25–33 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/processos/repositorio.py#L25-L33)

```python
    # ---- Update
    def atualizar(self, processo: Processo) -> None:
        self.banco.executar(
            """update processos set nome = :nome, status = :status, arquivo = :arquivo, formato = :formato,
                   total_traces = :total_traces, total_eventos = :total_eventos, atualizado_em = now()
               where id = :id""",
            id=processo.id, nome=processo.nome, status=processo.status, arquivo=processo.arquivo,
            formato=processo.formato, total_traces=processo.total_traces, total_eventos=processo.total_eventos,
        )
```

### Delete

`on delete cascade`: eventos, operações e análises do processo saem junto.

📍 `backend/driftor/processos/rotas.py` · linhas 107–111 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/processos/rotas.py#L107-L111)

```python
# ---- Delete
@rotas.post("/processos/{id}/excluir")
def excluir(id: str):
    RepositorioDeProcessos().excluir(id)
    return ir_para("/processos")
```

---

## 2. Atividade

| Operação | Requisição | Rota → regra → SQL |
|---|---|---|
| Create | `POST /atividades` | `criar` → `Atividade.criar` → `inserir` → `insert into atividades` |
| Read | `GET /atividades` | `listar` → `listar` (base) |
| Update | `POST /atividades/{id}` | `salvar` → `Atividade.editar` → `atualizar` → `update atividades` |
| Delete | `POST /atividades/{id}/excluir` | `excluir` → `excluir` → base, com `on delete restrict` |


### Create

📍 `backend/driftor/atividades/rotas.py` · linhas 20–24 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/atividades/rotas.py#L20-L24)

```python
# ---- Create
@rotas.post("/atividades")
def criar(nome: str = Form(""), descricao: str = Form("")):
    RepositorioDeAtividades().inserir(Atividade.criar(nome, descricao))
    return ir_para("/atividades")
```

📍 `backend/driftor/atividades/repositorio.py` · linhas 28–36 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/atividades/repositorio.py#L28-L36)

```python
    # ---- Create
    def inserir(self, atividade: Atividade) -> None:
        try:
            self.banco.executar(
                "insert into atividades (id, nome, descricao) values (:id, :nome, :descricao)",
                id=atividade.id, nome=atividade.nome, descricao=atividade.descricao,
            )
        except IntegrityError as erro:
            raise ErroDeNegocio(f"Já existe uma atividade chamada {atividade.nome}.") from erro
```

### Read

📍 `backend/driftor/atividades/rotas.py` · linhas 14–17 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/atividades/rotas.py#L14-L17)

```python
# ---- Read
@rotas.get("/atividades")
def listar(request: Request):
    return tela(request, "atividades/lista.html", atividades=RepositorioDeAtividades().listar())
```

### Update

📍 `backend/driftor/atividades/rotas.py` · linhas 34–40 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/atividades/rotas.py#L34-L40)

```python
@rotas.post("/atividades/{id}")
def salvar(id: str, nome: str = Form(""), descricao: str = Form("")):
    repo = RepositorioDeAtividades()
    atividade = repo.obter_ou_erro(id)
    atividade.editar(nome, descricao)
    repo.atualizar(atividade)
    return ir_para("/atividades")
```

📍 `backend/driftor/atividades/repositorio.py` · linhas 38–46 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/atividades/repositorio.py#L38-L46)

```python
    # ---- Update
    def atualizar(self, atividade: Atividade) -> None:
        try:
            self.banco.executar(
                "update atividades set nome = :nome, descricao = :descricao where id = :id",
                id=atividade.id, nome=atividade.nome, descricao=atividade.descricao,
            )
        except IntegrityError as erro:
            raise ErroDeNegocio(f"Já existe uma atividade chamada {atividade.nome}.") from erro
```

### Delete

`on delete restrict`: o banco recusa excluir uma atividade que algum processo usa, e o repositório transforma o erro em mensagem.

📍 `backend/driftor/atividades/rotas.py` · linhas 43–47 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/atividades/rotas.py#L43-L47)

```python
# ---- Delete
@rotas.post("/atividades/{id}/excluir")
def excluir(id: str):
    RepositorioDeAtividades().excluir(id)
    return ir_para("/atividades")
```

📍 `backend/driftor/atividades/repositorio.py` · linhas 48–53 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/atividades/repositorio.py#L48-L53)

```python
    # ---- Delete (o banco recusa se algum processo usa a atividade: on delete restrict)
    def excluir(self, id: str) -> None:
        try:
            super().excluir(id)
        except IntegrityError as erro:
            raise ErroDeNegocio("Esta atividade está mapeada em um processo e não pode ser excluída.") from erro
```

---

## 3. Análise

| Operação | Requisição | Rota → regra → SQL |
|---|---|---|
| Create | `POST /processos/{id}/analises` | `criar` → `Analise.criar`, `registrar_resultado` + Adapter ADWIN → `inserir` → `insert into analises` e `drifts` |
| Read (lista) | `GET /analises` | `listar` → `listar_resumo` |
| Read (detalhe) | `GET /analises/{id}` | `ver` → `obter_ou_erro` (base) + `criar_objeto` com os drifts |
| Update | `POST /analises/{id}/renomear` | `renomear` → `Analise.renomear` → `renomear` → `update analises` |
| Delete | `POST /analises/{id}/excluir` | `excluir` → `excluir` (base) → `delete from analises` |


### Create

📍 `backend/driftor/analises/rotas.py` · linhas 29–56 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/analises/rotas.py#L29-L56)

```python
# ---- Create: botão "Gerar análise de desvios" na página do processo
@rotas.post("/processos/{processo_id}/analises", dependencies=so_gestor)
def criar(
    processo_id: str,
    nome: str = Form(""),
    atividade: str = Form(""),
    delta: float = Form(0.002),
    tratamento: str = Form("bruto"),
    detector: DetectorDeDrift = Depends(detector),
):
    processos = RepositorioDeProcessos()
    processo = processos.obter_ou_erro(processo_id)
    analise = Analise.criar(processo, nome, delta, tratamento, atividade)

    pontos = PontoDaSerie.serie_de_duracao(processos.traces(processo_id), analise.atividade)
    if len(pontos) < 2:
        raise ErroDeNegocio("A série tem menos de duas observações.")
    valores = [p.valor for p in pontos]
    if tratamento == "tratado":
        valores = suavizar(valores)
    analise.registrar_resultado(valores, detector.detectar(valores, delta))  # Adapter em uso

    RepositorioDeAnalises().inserir(analise, valores)
    publicador_de_analise.notificar("analise_concluida", {  # Observer em uso
        "processo_id": processo_id,
        "mensagem": f"Análise “{analise.nome}” concluída: {len(analise.drifts)} desvio(s) encontrado(s).",
    })
    return ir_para(f"/analises/{analise.id}")
```

📍 `backend/driftor/analises/repositorio.py` · linhas 45–60 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/analises/repositorio.py#L45-L60)

```python
    # ---- Create
    def inserir(self, analise: Analise, serie: list[float]) -> None:
        self.banco.executar(
            """insert into analises (id, processo_id, nome, atividade, delta, tratamento,
                                     total_observacoes, total_drifts, serie)
               values (:id, :processo_id, :nome, :atividade, :delta, :tratamento,
                       :total_observacoes, :total_drifts, :serie)""",
            id=analise.id, processo_id=analise.processo_id, nome=analise.nome, atividade=analise.atividade,
            delta=analise.delta, tratamento=analise.tratamento, total_observacoes=analise.total_observacoes,
            total_drifts=len(analise.drifts), serie=json.dumps(serie),
        )
        self.banco.executar_varios(
            """insert into drifts (id, analise_id, posicao, indice, inicio_anomalia, media_antes, media_depois, variacao_pct)
               values (:id, :analise_id, :posicao, :indice, :inicio_anomalia, :media_antes, :media_depois, :variacao_pct)""",
            [{**vars(d), "analise_id": analise.id} for d in analise.drifts],
        )
```

### Read

📍 `backend/driftor/analises/rotas.py` · linhas 23–26 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/analises/rotas.py#L23-L26)

```python
# ---- Read: todas as análises
@rotas.get("/analises", dependencies=so_gestor)
def listar(request: Request):
    return tela(request, "analises/lista.html", analises=RepositorioDeAnalises().listar_resumo())
```

📍 `backend/driftor/analises/repositorio.py` · linhas 30–39 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/analises/repositorio.py#L30-L39)

```python
    # ---- Read
    def listar_resumo(self, processo_id: str | None = None) -> list[dict]:
        filtro = "where a.processo_id = :processo_id" if processo_id else ""
        return self.banco.consultar(
            f"""select a.id, a.nome, a.atividade, a.delta, a.tratamento, a.total_observacoes,
                       a.total_drifts, a.criado_em, p.nome as processo
                from analises a join processos p on p.id = a.processo_id
                {filtro} order by a.criado_em desc""",
            processo_id=processo_id,
        )
```

📍 `backend/driftor/analises/rotas.py` · linhas 59–67 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/analises/rotas.py#L59-L67)

```python
# ---- Read: detalhe com gráfico e desvios (o técnico também vê, sem editar)
@rotas.get("/analises/{id}", dependencies=[Depends(exigir("ver_analise"))])
def ver(request: Request, id: str):
    repo = RepositorioDeAnalises()
    analise = repo.obter_ou_erro(id)
    processo = RepositorioDeProcessos().obter(analise.processo_id)
    manutencoes = RepositorioDeManutencoes().listar_resumo(analise_id=id)
    return tela(request, "analises/detalhe.html", analise=analise, processo=processo, manutencoes=manutencoes,
                grafico=desenhar_grafico(repo.serie(id), [d.inicio_anomalia for d in analise.drifts]))
```

### Update

📍 `backend/driftor/analises/rotas.py` · linhas 70–77 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/analises/rotas.py#L70-L77)

```python
# ---- Update: renomear
@rotas.post("/analises/{id}/renomear", dependencies=so_gestor)
def renomear(id: str, nome: str = Form("")):
    repo = RepositorioDeAnalises()
    analise = repo.obter_ou_erro(id)
    analise.renomear(nome)
    repo.renomear(analise)
    return ir_para(f"/analises/{id}")
```

📍 `backend/driftor/analises/repositorio.py` · linhas 62–64 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/analises/repositorio.py#L62-L64)

```python
    # ---- Update
    def renomear(self, analise: Analise) -> None:
        self.banco.executar("update analises set nome = :nome where id = :id", id=analise.id, nome=analise.nome)
```

### Delete

`on delete cascade`: os drifts e as manutenções da análise saem junto.

📍 `backend/driftor/analises/rotas.py` · linhas 80–86 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/analises/rotas.py#L80-L86)

```python
# ---- Delete
@rotas.post("/analises/{id}/excluir", dependencies=so_gestor)
def excluir(id: str):
    repo = RepositorioDeAnalises()
    analise = repo.obter_ou_erro(id)
    repo.excluir(id)
    return ir_para(f"/processos/{analise.processo_id}")
```

---

## 4. Manutenção

| Operação | Requisição | Rota → regra → SQL |
|---|---|---|
| Create | `POST /analises/{id}/manutencoes` (Gestor) | `disparar` → `Manutencao.disparar` → `inserir` → `insert into manutencoes` |
| Read (lista) | `GET /manutencoes` (os dois) | `listar` → `listar_resumo` (join com análise, processo e drift) |
| Read (detalhe) | `GET /manutencoes/{id}` (os dois) | `ver` → `obter_ou_erro` (base) |
| Update (concluir) | `POST /manutencoes/{id}/concluir` (Técnico) | `concluir` → `Manutencao.concluir` → `atualizar` → `update manutencoes` |
| Update (descrição) | `POST /manutencoes/{id}` (Gestor) | `editar` → `Manutencao.editar` → `atualizar` |
| Delete | `POST /manutencoes/{id}/excluir` (Gestor) | `excluir` → `excluir` (base) → `delete from manutencoes` |


### Create

📍 `backend/driftor/manutencoes/rotas.py` · linhas 26–35 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/manutencoes/rotas.py#L26-L35)

```python
# ---- Create: o gestor dispara a manutenção na tela da análise
@rotas.post("/analises/{analise_id}/manutencoes", dependencies=[Depends(exigir("disparar_manutencao"))])
def disparar(analise_id: str, drift_id: str = Form(""), descricao: str = Form("")):
    analise = RepositorioDeAnalises().obter_ou_erro(analise_id)
    manutencao = Manutencao.disparar(analise, drift_id, descricao)
    RepositorioDeManutencoes().inserir(manutencao)
    publicador_de_manutencao.notificar("manutencao_disparada", {  # Observer: avisa o técnico
        "mensagem": f"Nova manutenção: {manutencao.descricao} (análise “{analise.nome}”).",
    })
    return ir_para(f"/analises/{analise_id}")
```

📍 `backend/driftor/manutencoes/repositorio.py` · linhas 41–48 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/manutencoes/repositorio.py#L41-L48)

```python
    # ---- Create
    def inserir(self, manutencao: Manutencao) -> None:
        self.banco.executar(
            """insert into manutencoes (id, analise_id, drift_id, descricao)
               values (:id, :analise_id, :drift_id, :descricao)""",
            id=manutencao.id, analise_id=manutencao.analise_id,
            drift_id=manutencao.drift_id, descricao=manutencao.descricao,
        )
```

### Read

📍 `backend/driftor/manutencoes/rotas.py` · linhas 20–23 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/manutencoes/rotas.py#L20-L23)

```python
# ---- Read: lista (gestor e técnico)
@rotas.get("/manutencoes", dependencies=[Depends(exigir("manutencoes"))])
def listar(request: Request):
    return tela(request, "manutencoes/lista.html", manutencoes=RepositorioDeManutencoes().listar_resumo())
```

📍 `backend/driftor/manutencoes/repositorio.py` · linhas 23–36 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/manutencoes/repositorio.py#L23-L36)

```python
    # ---- Read: a lista com o nome da análise, do processo e o número do desvio
    def listar_resumo(self, analise_id: str | None = None) -> list[dict]:
        filtro = "where m.analise_id = :analise_id" if analise_id else ""
        return self.banco.consultar(
            f"""select m.id, m.descricao, m.status, m.observacoes, m.criado_em, m.concluida_em,
                       a.id as analise_id, a.nome as analise, p.nome as processo, d.posicao as desvio
                from manutencoes m
                join analises a on a.id = m.analise_id
                join processos p on p.id = a.processo_id
                left join drifts d on d.id = m.drift_id
                {filtro}
                order by (m.status = 'pendente') desc, m.criado_em desc""",
            analise_id=analise_id,
        )
```

📍 `backend/driftor/manutencoes/rotas.py` · linhas 38–44 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/manutencoes/rotas.py#L38-L44)

```python
# ---- Read: detalhe (gestor e técnico)
@rotas.get("/manutencoes/{id}", dependencies=[Depends(exigir("manutencoes"))])
def ver(request: Request, id: str):
    manutencao = RepositorioDeManutencoes().obter_ou_erro(id)
    analise = RepositorioDeAnalises().obter_ou_erro(manutencao.analise_id)
    drift = next((d for d in analise.drifts if d.id == manutencao.drift_id), None)
    return tela(request, "manutencoes/detalhe.html", manutencao=manutencao, analise=analise, drift=drift)
```

### Update

📍 `backend/driftor/manutencoes/rotas.py` · linhas 47–57 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/manutencoes/rotas.py#L47-L57)

```python
# ---- Update pelo técnico: concluir com observações
@rotas.post("/manutencoes/{id}/concluir", dependencies=[Depends(exigir("concluir_manutencao"))])
def concluir(id: str, observacoes: str = Form("")):
    repo = RepositorioDeManutencoes()
    manutencao = repo.obter_ou_erro(id)
    manutencao.concluir(observacoes)
    repo.atualizar(manutencao)
    publicador_de_manutencao.notificar("manutencao_concluida", {  # Observer: avisa o gestor
        "mensagem": f"Manutenção concluída pelo técnico: {manutencao.descricao}.",
    })
    return ir_para("/manutencoes")
```

📍 `backend/driftor/manutencoes/rotas.py` · linhas 60–67 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/manutencoes/rotas.py#L60-L67)

```python
# ---- Update pelo gestor: corrigir a descrição enquanto está pendente
@rotas.post("/manutencoes/{id}", dependencies=[Depends(exigir("disparar_manutencao"))])
def editar(id: str, descricao: str = Form("")):
    repo = RepositorioDeManutencoes()
    manutencao = repo.obter_ou_erro(id)
    manutencao.editar(descricao)
    repo.atualizar(manutencao)
    return ir_para(f"/manutencoes/{id}")
```

📍 `backend/driftor/manutencoes/repositorio.py` · linhas 50–58 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/manutencoes/repositorio.py#L50-L58)

```python
    # ---- Update (o gestor edita a descrição; o técnico conclui com observações)
    def atualizar(self, manutencao: Manutencao) -> None:
        self.banco.executar(
            """update manutencoes set descricao = :descricao, status = :status, observacoes = :observacoes,
                   concluida_em = case when :status = 'concluida' then coalesce(concluida_em, now()) end
               where id = :id""",
            id=manutencao.id, descricao=manutencao.descricao,
            status=manutencao.status, observacoes=manutencao.observacoes,
        )
```

### Delete

📍 `backend/driftor/manutencoes/rotas.py` · linhas 70–74 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/manutencoes/rotas.py#L70-L74)

```python
# ---- Delete pelo gestor
@rotas.post("/manutencoes/{id}/excluir", dependencies=[Depends(exigir("disparar_manutencao"))])
def excluir(id: str):
    RepositorioDeManutencoes().excluir(id)
    return ir_para("/manutencoes")
```

---

## 5. Onde o SQL é executado

Os repositórios só montam o SQL. Quem executa é o `BancoDeDados` (Singleton): `consultar` para SELECT e `executar` para INSERT, UPDATE e DELETE.

📍 `backend/driftor/banco.py` · linhas 30–42 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/420f1db/backend/driftor/banco.py#L30-L42)

```python
    def consultar(self, sql: str, **parametros) -> list[dict]:
        """SELECT: devolve as linhas como dicionários."""
        with self.engine.connect() as conexao:
            return [dict(linha._mapping) for linha in conexao.execute(text(sql), parametros)]

    def consultar_um(self, sql: str, **parametros) -> dict | None:
        linhas = self.consultar(sql, **parametros)
        return linhas[0] if linhas else None

    def executar(self, sql: str, **parametros) -> int:
        """INSERT, UPDATE ou DELETE numa transação. Devolve quantas linhas mudaram."""
        with self.engine.begin() as conexao:
            return conexao.execute(text(sql), parametros).rowcount
```
