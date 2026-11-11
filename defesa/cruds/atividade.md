# CRUD de Atividade

[← CRUDs](README.md) · links fixos no commit `da31cd6`

Tela **Atividades**. As atividades também são criadas sozinhas quando um log é carregado (ver [Processo](processo.md#update-carregar-o-log)).

## Create: criar uma atividade

**1. Tela:** o botão **Criar atividade** manda o nome e a descrição.

📍 `frontend/src/telas/Atividades.jsx` · linhas 11–16 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/da31cd6/frontend/src/telas/Atividades.jsx#L11-L16)

```jsx
  const criar = async (e) => {
    e.preventDefault();
    await api("POST", "/atividades", nova);
    setNova({ nome: "", descricao: "" });
    carregar();
  };
```

**2. Controller:** recebe `POST /api/atividades`, confere o papel, cria o objeto e manda gravar.

📍 `atividade/AtividadeController.java` · linhas 23–28 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/da31cd6/backend/src/driftor/atividade/AtividadeController.java#L23-L28)

```java
    // ---- Create
    @PostMapping
    public void criar(@RequestHeader("Papel") String papel, @RequestBody Map<String, String> corpo) {
        Configuracao.getInstancia().exigir(papel, "atividades");
        repositorio.inserir(Atividade.criar(corpo.get("nome"), corpo.get("descricao")));
    }
```

**3. Domínio:** `Atividade.criar` gera o id e limpa os espaços.

📍 `dominio/Atividade.java` · linhas 16–18 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/da31cd6/backend/src/driftor/dominio/Atividade.java#L16-L18)

```java
    public static Atividade criar(String nome, String descricao) {
        return new Atividade(UUID.randomUUID(), nome.trim(), descricao.trim());
    }
```

**4. Banco:**

📍 `atividade/AtividadeRepositorio.java` · linhas 21–25 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/da31cd6/backend/src/driftor/atividade/AtividadeRepositorio.java#L21-L25)

```java
    // ---- Create
    public void inserir(Atividade atividade) {
        banco.executar("insert into atividades (id, nome, descricao) values (?, ?, ?)",
                atividade.getId(), atividade.getNome(), atividade.getDescricao());
    }
```

## Read: listar as atividades

**1. Tela:** ao abrir a tela, carrega a lista.

📍 `frontend/src/telas/Atividades.jsx` · linhas 8–8 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/da31cd6/frontend/src/telas/Atividades.jsx#L8-L8)

```jsx
  const carregar = () => api("GET", "/atividades").then(setAtividades);
```

**2. Controller:** `GET /api/atividades`.

📍 `atividade/AtividadeController.java` · linhas 16–21 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/da31cd6/backend/src/driftor/atividade/AtividadeController.java#L16-L21)

```java
    // ---- Read
    @GetMapping
    public List<Atividade> listar(@RequestHeader("Papel") String papel) {
        Configuracao.getInstancia().exigir(papel, "atividades");
        return repositorio.listar();
    }
```

**3. Banco:** o `listar` é herdado de `RepositorioBase` (compactação).

📍 `compactacao/RepositorioBase.java` · linhas 28–30 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/da31cd6/backend/src/driftor/compactacao/RepositorioBase.java#L28-L30)

```java
    public List<T> listar() {
        return banco.consultar("select " + colunas + " from " + tabela + " order by " + ordem, (linha, n) -> criarObjeto(linha));
    }
```

## Update: editar nome e descrição

**1. Tela:** o botão **Salvar** da linha manda o formulário.

📍 `frontend/src/telas/Atividades.jsx` · linhas 17–21 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/da31cd6/frontend/src/telas/Atividades.jsx#L17-L21)

```jsx
  const editar = async (e, id) => {
    e.preventDefault();
    await api("PUT", "/atividades/" + id, Object.fromEntries(new FormData(e.target)));
    carregar();
  };
```

**2. Controller:** `PUT /api/atividades/{id}`. Busca a atividade, aplica a mudança e grava.

📍 `atividade/AtividadeController.java` · linhas 30–37 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/da31cd6/backend/src/driftor/atividade/AtividadeController.java#L30-L37)

```java
    // ---- Update
    @PutMapping("/{id}")
    public void editar(@RequestHeader("Papel") String papel, @PathVariable UUID id, @RequestBody Map<String, String> corpo) {
        Configuracao.getInstancia().exigir(papel, "atividades");
        Atividade atividade = repositorio.obter(id);
        atividade.editar(corpo.get("nome"), corpo.get("descricao"));
        repositorio.atualizar(atividade);
    }
```

**3. Domínio:**

📍 `dominio/Atividade.java` · linhas 20–23 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/da31cd6/backend/src/driftor/dominio/Atividade.java#L20-L23)

```java
    public void editar(String nome, String descricao) {
        this.nome = nome.trim();
        this.descricao = descricao.trim();
    }
```

**4. Banco:**

📍 `atividade/AtividadeRepositorio.java` · linhas 27–31 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/da31cd6/backend/src/driftor/atividade/AtividadeRepositorio.java#L27-L31)

```java
    // ---- Update
    public void atualizar(Atividade atividade) {
        banco.executar("update atividades set nome = ?, descricao = ? where id = ?",
                atividade.getNome(), atividade.getDescricao(), atividade.getId());
    }
```

## Delete: excluir

**1. Tela:**

📍 `frontend/src/telas/Atividades.jsx` · linhas 22–22 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/da31cd6/frontend/src/telas/Atividades.jsx#L22-L22)

```jsx
  const excluir = async (id) => { await api("DELETE", "/atividades/" + id); carregar(); };
```

**2. Controller:** `DELETE /api/atividades/{id}`.

📍 `atividade/AtividadeController.java` · linhas 39–44 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/da31cd6/backend/src/driftor/atividade/AtividadeController.java#L39-L44)

```java
    // ---- Delete
    @DeleteMapping("/{id}")
    public void excluir(@RequestHeader("Papel") String papel, @PathVariable UUID id) {
        Configuracao.getInstancia().exigir(papel, "atividades");
        repositorio.excluir(id);
    }
```

**3. Banco:** o `excluir` é herdado de `RepositorioBase`. Os eventos dessa atividade saem junto (`on delete cascade`).

📍 `compactacao/RepositorioBase.java` · linhas 37–39 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/da31cd6/backend/src/driftor/compactacao/RepositorioBase.java#L37-L39)

```java
    public void excluir(UUID id) {
        banco.executar("delete from " + tabela + " where id = ?", id);
    }
```
