# CRUD de Processo

[← CRUDs](README.md) · links fixos no commit `e994f19`

Telas **Processos** (lista) e **Processo** (detalhe).

## Create: criar um processo

**1. Tela:** o botão **Criar processo** manda o nome e abre o processo novo.

📍 `frontend/src/telas/Processos.jsx` · linhas 13–17 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/e994f19/frontend/src/telas/Processos.jsx#L13-L17)

```jsx
  const criar = async (e) => {
    e.preventDefault();
    const processo = await api("POST", "/processos", { nome });
    navegar("/processos/" + processo.id);
  };
```

**2. Controller:** `POST /api/processos`.

📍 `processo/ProcessoController.java` · linhas 31–38 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/e994f19/backend/src/driftor/processo/ProcessoController.java#L31-L38)

```java
    // ---- Create
    @PostMapping
    public Processo criar(@RequestHeader("Papel") String papel, @RequestBody Map<String, String> corpo) {
        Configuracao.getInstancia().exigir(papel, "processos");
        Processo processo = Processo.criar(corpo.get("nome"));
        repositorio.inserir(processo);
        return processo;
    }
```

**3. Domínio:**

📍 `dominio/Processo.java` · linhas 21–23 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/e994f19/backend/src/driftor/dominio/Processo.java#L21-L23)

```java
    public static Processo criar(String nome) {
        return new Processo(UUID.randomUUID(), nome.trim(), null, 0, 0);
    }
```

**4. Banco:**

📍 `processo/ProcessoRepositorio.java` · linhas 28–31 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/e994f19/backend/src/driftor/processo/ProcessoRepositorio.java#L28-L31)

```java
    // ---- Create
    public void inserir(Processo processo) {
        banco.executar("insert into processos (id, nome) values (?, ?)", processo.getId(), processo.getNome());
    }
```

## Read: ver o processo com o grafo

**1. Tela:**

📍 `frontend/src/telas/Processo.jsx` · linhas 17–17 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/e994f19/frontend/src/telas/Processo.jsx#L17-L17)

```jsx
  const carregar = () => api("GET", "/processos/" + id).then(setDados);
```

**2. Controller:** `GET /api/processos/{id}`. Lê os traces do banco, pede as arestas ao minerador ([Adapter](../padroes/adapter.md)) e monta o grafo e as variantes.

📍 `processo/ProcessoController.java` · linhas 40–48 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/e994f19/backend/src/driftor/processo/ProcessoController.java#L40-L48)

```java
    // ---- Read: detalhe com o grafo, as variantes e as análises
    @GetMapping("/{id}")
    public Map<String, Object> ver(@RequestHeader("Papel") String papel, @PathVariable UUID id) {
        Configuracao.getInstancia().exigir(papel, "processos");
        List<Trace> traces = repositorio.traces(id);
        Grafo grafo = Grafo.montar(traces, traces.isEmpty() ? List.of() : minerador.descobrirArestas(traces));
        return Map.of("processo", repositorio.obter(id), "mermaid", grafo.paraMermaid(), "atividades", grafo.getNos(),
                "variantes", Variante.agrupar(traces), "analises", new AnaliseRepositorio().doProcesso(id));
    }
```

**3. Banco:** os eventos voltam ligados ao nome da atividade.

📍 `processo/ProcessoRepositorio.java` · linhas 58–69 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/e994f19/backend/src/driftor/processo/ProcessoRepositorio.java#L58-L69)

```java
    // ---- Read: os traces voltam montados a partir dos eventos
    public List<Trace> traces(UUID processoId) {
        Map<String, Trace> traces = new LinkedHashMap<>();
        banco.consultar("""
                select e.case_id, a.nome, e.inicio, e.duracao from eventos e join atividades a on a.id = e.atividade_id
                where e.processo_id = ? order by e.case_id, e.ordem""", (linha, n) -> {
            traces.computeIfAbsent(linha.getString("case_id"), Trace::new).adicionar(new Evento(
                    linha.getString("nome"), linha.getObject("inicio", java.time.OffsetDateTime.class), linha.getDouble("duracao")));
            return null;
        }, processoId);
        return new ArrayList<>(traces.values());
    }
```

A lista de processos (`GET /api/processos`) usa o `listar` herdado de `RepositorioBase`.

## Update: carregar o log

**1. Tela:** o botão **Carregar** envia o arquivo `.xes`.

📍 `frontend/src/telas/Processo.jsx` · linhas 25–29 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/e994f19/frontend/src/telas/Processo.jsx#L25-L29)

```jsx
  const carregarLog = async (e) => {
    e.preventDefault();
    await api("POST", `/processos/${id}/log`, new FormData(e.target));
    carregar();
  };
```

**2. Controller:** `POST /api/processos/{id}/log`. O motor lê o arquivo e devolve os traces; o processo guarda os totais.

📍 `processo/ProcessoController.java` · linhas 50–58 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/e994f19/backend/src/driftor/processo/ProcessoController.java#L50-L58)

```java
    // ---- Update: carregar o log (as atividades aparecem direto no grafo)
    @PostMapping("/{id}/log")
    public void carregarLog(@RequestHeader("Papel") String papel, @PathVariable UUID id, @RequestParam MultipartFile arquivo) {
        Configuracao.getInstancia().exigir(papel, "processos");
        Processo processo = repositorio.obter(id);
        List<Trace> traces = LeitorDeLog.ler(arquivo);
        processo.carregarLog(arquivo.getOriginalFilename(), traces);
        repositorio.salvarLog(processo, traces);
    }
```

**3. Banco:** cria as atividades que ainda não existem e grava os eventos ligados a elas.

📍 `processo/ProcessoRepositorio.java` · linhas 40–56 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/e994f19/backend/src/driftor/processo/ProcessoRepositorio.java#L40-L56)

```java
    public void salvarLog(Processo processo, List<Trace> traces) {
        List<Object[]> eventos = new ArrayList<>();
        for (Trace trace : traces) {
            for (int ordem = 0; ordem < trace.getEventos().size(); ordem++) {
                Evento e = trace.getEventos().get(ordem);
                eventos.add(new Object[] {processo.getId(), trace.getCaseId(), ordem, e.getInicio(), e.getDuracao(), e.getAtividade()});
            }
        }
        List<Object[]> atividades = eventos.stream().map(e -> e[5]).distinct()
                .map(nome -> new Object[] {UUID.randomUUID(), nome}).toList();
        banco.executarVarios("insert into atividades (id, nome) values (?, ?) on conflict (nome) do nothing", atividades);
        banco.executar("delete from eventos where processo_id = ?", processo.getId());
        banco.executarVarios("""
                insert into eventos (processo_id, case_id, ordem, inicio, duracao, atividade_id)
                select ?, ?, ?, ?, ?, id from atividades where nome = ?""", eventos);
        atualizar(processo);
    }
```

## Update: renomear

📍 `frontend/src/telas/Processo.jsx` · linhas 30–30 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/e994f19/frontend/src/telas/Processo.jsx#L30-L30)

```jsx
  const renomear = async (nome) => { await api("PUT", "/processos/" + id, { nome }); carregar(); };
```

📍 `processo/ProcessoController.java` · linhas 60–67 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/e994f19/backend/src/driftor/processo/ProcessoController.java#L60-L67)

```java
    // ---- Update: renomear
    @PutMapping("/{id}")
    public void renomear(@RequestHeader("Papel") String papel, @PathVariable UUID id, @RequestBody Map<String, String> corpo) {
        Configuracao.getInstancia().exigir(papel, "processos");
        Processo processo = repositorio.obter(id);
        processo.renomear(corpo.get("nome"));
        repositorio.atualizar(processo);
    }
```

📍 `processo/ProcessoRepositorio.java` · linhas 33–37 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/e994f19/backend/src/driftor/processo/ProcessoRepositorio.java#L33-L37)

```java
    // ---- Update
    public void atualizar(Processo processo) {
        banco.executar("update processos set nome = ?, arquivo = ?, total_traces = ?, total_eventos = ? where id = ?",
                processo.getNome(), processo.getArquivo(), processo.getTotalTraces(), processo.getTotalEventos(), processo.getId());
    }
```

## Delete: excluir

📍 `frontend/src/telas/Processo.jsx` · linhas 31–31 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/e994f19/frontend/src/telas/Processo.jsx#L31-L31)

```jsx
  const excluir = async () => { await api("DELETE", "/processos/" + id); navegar("/processos"); };
```

📍 `processo/ProcessoController.java` · linhas 69–74 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/e994f19/backend/src/driftor/processo/ProcessoController.java#L69-L74)

```java
    // ---- Delete
    @DeleteMapping("/{id}")
    public void excluir(@RequestHeader("Papel") String papel, @PathVariable UUID id) {
        Configuracao.getInstancia().exigir(papel, "processos");
        repositorio.excluir(id);
    }
```

O `excluir` é herdado de `RepositorioBase`. Eventos e análises do processo saem junto (`on delete cascade`).
