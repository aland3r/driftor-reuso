# CRUD de Manutenção

[← CRUDs](README.md) · links fixos no commit `21ee145`

O gestor dispara a manutenção na tela **Análise**. O técnico conclui na tela **Manutenção**.

## Create: disparar a manutenção (gestor)

**1. Tela:** o botão **Disparar manutenção** de um desvio manda a descrição.

📍 `frontend/src/telas/Analise.jsx` · linhas 20–24 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/21ee145/frontend/src/telas/Analise.jsx#L20-L24)

```jsx
  const disparar = async (driftId) => {
    await api("POST", `/analises/${id}/manutencoes`, { driftId, descricao });
    setDescricao("");
    carregar();
  };
```

**2. Controller:** `POST /api/analises/{id}/manutencoes`. Grava e avisa o técnico ([Observer](../padroes/observer.md)).

📍 `manutencao/ManutencaoController.java` · linhas 24–31 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/manutencao/ManutencaoController.java#L24-L31)

```java
    // ---- Create: o gestor dispara a partir de um desvio
    @PostMapping("/api/analises/{analiseId}/manutencoes")
    public void disparar(@RequestHeader("Papel") String papel, @PathVariable UUID analiseId, @RequestBody Map<String, String> corpo) {
        Configuracao.getInstancia().exigir(papel, "disparar_manutencao");
        Manutencao manutencao = Manutencao.disparar(analiseId, UUID.fromString(corpo.get("driftId")), corpo.get("descricao"));
        repositorio.inserir(manutencao);
        Avisos.MANUTENCAO.notificar("manutencao_disparada", "Nova manutenção: " + manutencao.getDescricao());  // Observer
    }
```

**3. Domínio:**

📍 `dominio/Manutencao.java` · linhas 23–25 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/dominio/Manutencao.java#L23-L25)

```java
    public static Manutencao disparar(UUID analiseId, UUID driftId, String descricao) {
        return new Manutencao(UUID.randomUUID(), analiseId, driftId, descricao.trim(), "pendente", "");
    }
```

**4. Banco:**

📍 `manutencao/ManutencaoRepositorio.java` · linhas 34–38 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/manutencao/ManutencaoRepositorio.java#L34-L38)

```java
    // ---- Create
    public void inserir(Manutencao manutencao) {
        banco.executar("insert into manutencoes (id, analise_id, drift_id, descricao) values (?, ?, ?, ?)",
                manutencao.getId(), manutencao.getAnaliseId(), manutencao.getDriftId(), manutencao.getDescricao());
    }
```

## Read: lista de manutenções

📍 `frontend/src/telas/Manutencoes.jsx` · linhas 9–9 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/21ee145/frontend/src/telas/Manutencoes.jsx#L9-L9)

```jsx
  const carregar = () => api("GET", "/manutencoes").then(setManutencoes);
```

📍 `manutencao/ManutencaoController.java` · linhas 17–22 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/manutencao/ManutencaoController.java#L17-L22)

```java
    // ---- Read: lista (gestor e técnico)
    @GetMapping("/api/manutencoes")
    public List<Map<String, Object>> listar(@RequestHeader("Papel") String papel) {
        Configuracao.getInstancia().exigir(papel, "manutencoes");
        return repositorio.listarResumo(null);
    }
```

**Banco:** a lista junta o nome da análise, do processo e o número do desvio.

📍 `manutencao/ManutencaoRepositorio.java` · linhas 25–32 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/manutencao/ManutencaoRepositorio.java#L25-L32)

```java
    // ---- Read: a lista com o nome da análise, do processo e o número do desvio
    public List<Map<String, Object>> listarResumo(UUID analiseId) {
        return banco.consultarLinhas("""
                select m.id, m.drift_id, m.descricao, m.status, a.id as analise_id, a.nome as analise, p.nome as processo, d.posicao as desvio
                from manutencoes m join analises a on a.id = m.analise_id join processos p on p.id = a.processo_id
                join drifts d on d.id = m.drift_id
                where ?::uuid is null or m.analise_id = ? order by m.status desc""", analiseId, analiseId);
    }
```

## Update: concluir (técnico)

**1. Tela:** o botão **Marcar como concluída** manda as observações.

📍 `frontend/src/telas/Manutencao.jsx` · linhas 15–19 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/21ee145/frontend/src/telas/Manutencao.jsx#L15-L19)

```jsx
  const concluir = async (e) => {
    e.preventDefault();
    await api("PUT", `/manutencoes/${id}/concluir`, { observacoes });
    carregar();
  };
```

**2. Controller:** `PUT /api/manutencoes/{id}/concluir`. Grava e avisa o gestor ([Observer](../padroes/observer.md)).

📍 `manutencao/ManutencaoController.java` · linhas 41–49 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/manutencao/ManutencaoController.java#L41-L49)

```java
    // ---- Update: o técnico conclui com as observações
    @PutMapping("/api/manutencoes/{id}/concluir")
    public void concluir(@RequestHeader("Papel") String papel, @PathVariable UUID id, @RequestBody Map<String, String> corpo) {
        Configuracao.getInstancia().exigir(papel, "concluir_manutencao");
        Manutencao manutencao = repositorio.obter(id);
        manutencao.concluir(corpo.get("observacoes"));
        repositorio.atualizar(manutencao);
        Avisos.MANUTENCAO.notificar("manutencao_concluida", "Manutenção concluída: " + manutencao.getDescricao());  // Observer
    }
```

**3. Domínio:**

📍 `dominio/Manutencao.java` · linhas 31–34 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/dominio/Manutencao.java#L31-L34)

```java
    public void concluir(String observacoes) {
        this.status = "concluída";
        this.observacoes = observacoes.trim();
    }
```

**4. Banco:**

📍 `manutencao/ManutencaoRepositorio.java` · linhas 40–44 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/manutencao/ManutencaoRepositorio.java#L40-L44)

```java
    // ---- Update
    public void atualizar(Manutencao manutencao) {
        banco.executar("update manutencoes set status = ?, observacoes = ? where id = ?",
                manutencao.getStatus(), manutencao.getObservacoes(), manutencao.getId());
    }
```

## Delete: excluir (gestor)

📍 `frontend/src/telas/Manutencoes.jsx` · linhas 11–11 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/21ee145/frontend/src/telas/Manutencoes.jsx#L11-L11)

```jsx
  const excluir = async (id) => { await api("DELETE", "/manutencoes/" + id); carregar(); };
```

📍 `manutencao/ManutencaoController.java` · linhas 51–56 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/manutencao/ManutencaoController.java#L51-L56)

```java
    // ---- Delete: só o gestor
    @DeleteMapping("/api/manutencoes/{id}")
    public void excluir(@RequestHeader("Papel") String papel, @PathVariable UUID id) {
        Configuracao.getInstancia().exigir(papel, "disparar_manutencao");
        repositorio.excluir(id);
    }
```

O `excluir` é herdado de `RepositorioBase`.
