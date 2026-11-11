# CRUD de Atividade

[← CRUDs](README.md) · links fixos no commit `21ee145`

Tela **Atividades**. As atividades também são criadas sozinhas quando um log é carregado (ver [Processo](processo.md#update-carregar-o-log)).

## Create: criar uma atividade

**1. Tela:** o botão **Criar atividade** manda o nome.

📍 `frontend/src/telas/Atividades.jsx` · linhas 11–16 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/21ee145/frontend/src/telas/Atividades.jsx#L11-L16)

```jsx
  const criar = async (e) => {
    e.preventDefault();
    await api("POST", "/atividades", { nome });
    setNome("");
    carregar();
  };
```

**2. Controller:** recebe `POST /api/atividades`, confere o papel, cria o objeto e manda gravar.

📍 `atividade/AtividadeController.java` · linhas 23–28 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/atividade/AtividadeController.java#L23-L28)

```java
    // ---- Create
    @PostMapping
    public void criar(@RequestHeader("Papel") String papel, @RequestBody Map<String, String> corpo) {
        Configuracao.getInstancia().exigir(papel, "atividades");
        repositorio.inserir(Atividade.criar(corpo.get("nome")));
    }
```

**3. Domínio:** `Atividade.criar` gera o id e limpa os espaços.

📍 `dominio/Atividade.java` · linhas 14–16 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/dominio/Atividade.java#L14-L16)

```java
    public static Atividade criar(String nome) {
        return new Atividade(UUID.randomUUID(), nome.trim());
    }
```

**4. Banco:**

📍 `atividade/AtividadeRepositorio.java` · linhas 21–24 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/atividade/AtividadeRepositorio.java#L21-L24)

```java
    // ---- Create
    public void inserir(Atividade atividade) {
        banco.executar("insert into atividades (id, nome) values (?, ?)", atividade.getId(), atividade.getNome());
    }
```

## Read: listar as atividades

**1. Tela:** ao abrir a tela, carrega a lista.

📍 `frontend/src/telas/Atividades.jsx` · linhas 8–8 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/21ee145/frontend/src/telas/Atividades.jsx#L8-L8)

```jsx
  const carregar = () => api("GET", "/atividades").then(setAtividades);
```

**2. Controller:** `GET /api/atividades`.

📍 `atividade/AtividadeController.java` · linhas 16–21 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/atividade/AtividadeController.java#L16-L21)

```java
    // ---- Read
    @GetMapping
    public List<Atividade> listar(@RequestHeader("Papel") String papel) {
        Configuracao.getInstancia().exigir(papel, "atividades");
        return repositorio.listar();
    }
```

**3. Banco:** o `listar` é herdado de `RepositorioBase` (compactação).

📍 `compactacao/RepositorioBase.java` · linhas 28–30 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/compactacao/RepositorioBase.java#L28-L30)

```java
    public List<T> listar() {
        return banco.consultar("select " + colunas + " from " + tabela + " order by " + ordem, (linha, n) -> criarObjeto(linha));
    }
```

## Update: renomear

**1. Tela:** o botão **Renomear** da linha manda o nome novo.

📍 `frontend/src/telas/Atividades.jsx` · linhas 17–21 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/21ee145/frontend/src/telas/Atividades.jsx#L17-L21)

```jsx
  const renomear = async (e, id) => {
    e.preventDefault();
    await api("PUT", "/atividades/" + id, Object.fromEntries(new FormData(e.target)));
    carregar();
  };
```

**2. Controller:** `PUT /api/atividades/{id}`. Busca a atividade, aplica a mudança e grava.

📍 `atividade/AtividadeController.java` · linhas 30–37 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/atividade/AtividadeController.java#L30-L37)

```java
    // ---- Update
    @PutMapping("/{id}")
    public void renomear(@RequestHeader("Papel") String papel, @PathVariable UUID id, @RequestBody Map<String, String> corpo) {
        Configuracao.getInstancia().exigir(papel, "atividades");
        Atividade atividade = repositorio.obter(id);
        atividade.renomear(corpo.get("nome"));
        repositorio.atualizar(atividade);
    }
```

**3. Domínio:**

📍 `dominio/Atividade.java` · linhas 18–20 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/dominio/Atividade.java#L18-L20)

```java
    public void renomear(String novoNome) {
        this.nome = novoNome.trim();
    }
```

**4. Banco:**

📍 `atividade/AtividadeRepositorio.java` · linhas 26–29 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/atividade/AtividadeRepositorio.java#L26-L29)

```java
    // ---- Update
    public void atualizar(Atividade atividade) {
        banco.executar("update atividades set nome = ? where id = ?", atividade.getNome(), atividade.getId());
    }
```

## Delete: excluir

**1. Tela:**

📍 `frontend/src/telas/Atividades.jsx` · linhas 22–22 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/21ee145/frontend/src/telas/Atividades.jsx#L22-L22)

```jsx
  const excluir = async (id) => { await api("DELETE", "/atividades/" + id); carregar(); };
```

**2. Controller:** `DELETE /api/atividades/{id}`.

📍 `atividade/AtividadeController.java` · linhas 39–44 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/atividade/AtividadeController.java#L39-L44)

```java
    // ---- Delete
    @DeleteMapping("/{id}")
    public void excluir(@RequestHeader("Papel") String papel, @PathVariable UUID id) {
        Configuracao.getInstancia().exigir(papel, "atividades");
        repositorio.excluir(id);
    }
```

**3. Banco:** o `excluir` é herdado de `RepositorioBase`. Os eventos dessa atividade saem junto (`on delete cascade`).

📍 `compactacao/RepositorioBase.java` · linhas 37–39 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/compactacao/RepositorioBase.java#L37-L39)

```java
    public void excluir(UUID id) {
        banco.executar("delete from " + tabela + " where id = ?", id);
    }
```
