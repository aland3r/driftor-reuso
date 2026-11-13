# CRUD de Análise

[← CRUDs](README.md) · links fixos no commit `bee4987`

A análise nasce na tela do **Processo** e abre na tela **Análise**.

## Create: gerar a análise de desvios

**1. Tela:** o botão **Gerar análise de desvios** manda a atividade e o δ.

📍 `frontend/src/telas/Processo.jsx` · [linhas 32–36](https://github.com/aland3r/driftor-reuso/blob/bee4987/frontend/src/telas/Processo.jsx#L32-L36)

```jsx
  const gerarAnalise = async (e) => {
    e.preventDefault();
    const analise = await api("POST", `/processos/${id}/analises`, { atividade, delta });
    navegar("/analises/" + analise.id);
  };
```

**2. Controller:** `POST /api/processos/{id}/analises`. Monta a série, pede os desvios ao detector ([Adapter](../padroes/adapter.md)), grava e avisa o gestor ([Observer](../padroes/observer.md)).

📍 `analise/AnaliseController.java` · [linhas 23–37](https://github.com/aland3r/driftor-reuso/blob/bee4987/backend/src/driftor/analise/AnaliseController.java#L23-L37)

```java
    // ---- Create: "Gerar análise de desvios" na página do processo
    @PostMapping("/api/processos/{processoId}/analises")
    public Analise criar(@RequestHeader("Papel") String papel, @PathVariable UUID processoId, @RequestBody Map<String, String> corpo) {
        Configuracao.getInstancia().exigir(papel, "analises");
        ProcessoRepositorio processos = new ProcessoRepositorio();
        Processo processo = processos.obter(processoId);
        Analise analise = Analise.criar(processo, corpo.get("atividade"), Double.parseDouble(corpo.get("delta")));
        List<PontoDaSerie> serie = PontoDaSerie.serieDeDuracao(processos.traces(processoId), analise.getAtividade());
        List<Double> valores = serie.stream().map(PontoDaSerie::getValor).toList();
        analise.registrarResultado(valores, detector.detectar(serie, analise.getDelta()));  // Adapter
        repositorio.inserir(analise, valores);
        Avisos.ANALISE.notificar("analise_concluida",  // Observer
                "Análise " + analise.getNome() + " concluída: " + analise.getDrifts().size() + " desvio(s).");
        return analise;
    }
```

**3. Domínio:** calcula a média antes e depois de cada desvio.

📍 `dominio/Analise.java` · [linhas 36–46](https://github.com/aland3r/driftor-reuso/blob/bee4987/backend/src/driftor/dominio/Analise.java#L36-L46)

```java
    public void registrarResultado(List<Double> valores, List<Integer> inicios) {
        totalObservacoes = valores.size();
        drifts = new ArrayList<>();
        for (int i = 0; i < inicios.size(); i++) {
            int comeco = i == 0 ? 0 : inicios.get(i - 1);
            int fim = i + 1 < inicios.size() ? inicios.get(i + 1) : valores.size();
            int inicio = inicios.get(i);
            drifts.add(new Drift(UUID.randomUUID(), i + 1, inicio,
                    media(valores.subList(comeco, inicio)), media(valores.subList(inicio, fim))));
        }
    }
```

**4. Banco:** grava a análise e os seus desvios.

📍 `analise/AnaliseRepositorio.java` · [linhas 44–52](https://github.com/aland3r/driftor-reuso/blob/bee4987/backend/src/driftor/analise/AnaliseRepositorio.java#L44-L52)

```java
    // ---- Create
    public void inserir(Analise analise, List<Double> serie) {
        banco.executar("insert into analises (id, processo_id, nome, atividade, delta, total_observacoes, serie) values (?, ?, ?, ?, ?, ?, ?)",
                analise.getId(), analise.getProcessoId(), analise.getNome(), analise.getAtividade(), analise.getDelta(),
                analise.getTotalObservacoes(), serie.stream().map(String::valueOf).collect(Collectors.joining(",")));
        banco.executarVarios("insert into drifts (id, analise_id, posicao, inicio, media_antes, media_depois) values (?, ?, ?, ?, ?, ?)",
                analise.getDrifts().stream().map(d -> new Object[] {d.getId(), analise.getId(), d.getPosicao(), d.getInicio(),
                        d.getMediaAntes(), d.getMediaDepois()}).toList());
    }
```

## Read: ver a análise

📍 `frontend/src/telas/Analise.jsx` · [linhas 12–12](https://github.com/aland3r/driftor-reuso/blob/bee4987/frontend/src/telas/Analise.jsx#L12-L12)

```jsx
  const carregar = () => api("GET", "/analises/" + id).then(setDados);
```

📍 `analise/AnaliseController.java` · [linhas 39–46](https://github.com/aland3r/driftor-reuso/blob/bee4987/backend/src/driftor/analise/AnaliseController.java#L39-L46)

```java
    // ---- Read: detalhe com a série e os desvios (o técnico também vê)
    @GetMapping("/api/analises/{id}")
    public Map<String, Object> ver(@RequestHeader("Papel") String papel, @PathVariable UUID id) {
        Configuracao.getInstancia().exigir(papel, "ver_analise");
        Analise analise = repositorio.obter(id);
        return Map.of("analise", analise, "processo", new ProcessoRepositorio().obter(analise.getProcessoId()),
                "serie", repositorio.serie(id), "manutencoes", new ManutencaoRepositorio().listarResumo(id));
    }
```

**Banco:** `obter` é herdado de `RepositorioBase`; os desvios vêm junto em `criarObjeto`.

📍 `analise/AnaliseRepositorio.java` · [linhas 22–31](https://github.com/aland3r/driftor-reuso/blob/bee4987/backend/src/driftor/analise/AnaliseRepositorio.java#L22-L31)

```java
    protected Analise criarObjeto(ResultSet linha) throws SQLException {
        Analise analise = new Analise(linha.getObject("id", UUID.class), linha.getObject("processo_id", UUID.class),
                linha.getString("nome"), linha.getString("atividade"), linha.getDouble("delta"), linha.getInt("total_observacoes"));
        analise.setDrifts(banco.consultar(
                "select id, posicao, inicio, media_antes, media_depois from drifts where analise_id = ? order by posicao",
                (d, n) -> new Drift(d.getObject("id", UUID.class), d.getInt("posicao"), d.getInt("inicio"),
                        d.getDouble("media_antes"), d.getDouble("media_depois")),
                analise.getId()));
        return analise;
    }
```

## Update: renomear

📍 `frontend/src/telas/Analise.jsx` · [linhas 18–18](https://github.com/aland3r/driftor-reuso/blob/bee4987/frontend/src/telas/Analise.jsx#L18-L18)

```jsx
  const renomear = async (nome) => { await api("PUT", "/analises/" + id, { nome }); carregar(); };
```

📍 `analise/AnaliseController.java` · [linhas 48–55](https://github.com/aland3r/driftor-reuso/blob/bee4987/backend/src/driftor/analise/AnaliseController.java#L48-L55)

```java
    // ---- Update: renomear
    @PutMapping("/api/analises/{id}")
    public void renomear(@RequestHeader("Papel") String papel, @PathVariable UUID id, @RequestBody Map<String, String> corpo) {
        Configuracao.getInstancia().exigir(papel, "analises");
        Analise analise = repositorio.obter(id);
        analise.renomear(corpo.get("nome"));
        repositorio.renomear(analise);
    }
```

📍 `analise/AnaliseRepositorio.java` · [linhas 54–57](https://github.com/aland3r/driftor-reuso/blob/bee4987/backend/src/driftor/analise/AnaliseRepositorio.java#L54-L57)

```java
    // ---- Update
    public void renomear(Analise analise) {
        banco.executar("update analises set nome = ? where id = ?", analise.getNome(), analise.getId());
    }
```

## Delete: excluir

📍 `frontend/src/telas/Analise.jsx` · [linhas 19–19](https://github.com/aland3r/driftor-reuso/blob/bee4987/frontend/src/telas/Analise.jsx#L19-L19)

```jsx
  const excluir = async () => { await api("DELETE", "/analises/" + id); navegar("/processos/" + processo.id); };
```

📍 `analise/AnaliseController.java` · [linhas 57–62](https://github.com/aland3r/driftor-reuso/blob/bee4987/backend/src/driftor/analise/AnaliseController.java#L57-L62)

```java
    // ---- Delete
    @DeleteMapping("/api/analises/{id}")
    public void excluir(@RequestHeader("Papel") String papel, @PathVariable UUID id) {
        Configuracao.getInstancia().exigir(papel, "analises");
        repositorio.excluir(id);
    }
```

O `excluir` é herdado de `RepositorioBase`. Desvios e manutenções saem junto (`on delete cascade`).
