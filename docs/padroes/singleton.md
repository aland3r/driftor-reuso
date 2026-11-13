# Singleton

[← docs](../README.md) · links fixos no commit `7c48276`

**O que é:** garante que uma classe tenha **uma única instância** e dá um ponto de acesso global a ela.

**Como se monta:** construtor **privado** (ninguém faz `new`), um atributo **estático** com a instância e um método **estático** `getInstancia()` que cria na primeira chamada e devolve sempre a mesma.

**Por que usamos:** o app inteiro usa **uma** conexão (pool) com o banco.

## Exemplo: BancoDeDados, no caminho de "Criar atividade"

**1. Tela:** o botão **Criar atividade** chama a API.

📍 `frontend/src/telas/Atividades.jsx` · [linhas 11–16](https://github.com/aland3r/driftor-reuso/blob/7c48276/frontend/src/telas/Atividades.jsx#L11-L16)

```jsx
  const criar = async (e) => {
    e.preventDefault();
    await api("POST", "/atividades", { nome });
    setNome("");
    carregar();
  };
```

**2. Controller:** pede ao repositório para gravar.

📍 `atividade/AtividadeController.java` · [linhas 23–28](https://github.com/aland3r/driftor-reuso/blob/7c48276/backend/src/driftor/atividade/AtividadeController.java#L23-L28)

```java
    // ---- Create
    @PostMapping
    public void criar(@RequestHeader("Papel") String papel, @RequestBody Map<String, String> corpo) {
        Configuracao.getInstancia().exigir(papel, "atividades");  // SINGLETON (Configuracao) + VARIABILIDADE: sem permissão, 403
        repositorio.inserir(Atividade.criar(corpo.get("nome")));
    }
```

**3. Repositório:** todo repositório pega o banco com `getInstancia()`; esse atributo está em `RepositorioBase`.

📍 `compactacao/RepositorioBase.java` · [linhas 19–19](https://github.com/aland3r/driftor-reuso/blob/7c48276/backend/src/driftor/compactacao/RepositorioBase.java#L19-L19)

```java
    protected final BancoDeDados banco = BancoDeDados.getInstancia();
```

📍 `atividade/AtividadeRepositorio.java` · [linhas 23–26](https://github.com/aland3r/driftor-reuso/blob/7c48276/backend/src/driftor/atividade/AtividadeRepositorio.java#L23-L26)

```java
    // ---- Create
    public void inserir(Atividade atividade) {
        banco.executar("insert into atividades (id, nome) values (?, ?)", atividade.getId(), atividade.getNome());
    }
```

**4. Singleton:** o construtor é privado e `getInstancia()` só cria o objeto na primeira vez.

📍 `singleton/BancoDeDados.java` · [linhas 18–18](https://github.com/aland3r/driftor-reuso/blob/7c48276/backend/src/driftor/singleton/BancoDeDados.java#L18-L18)

```java
    private static BancoDeDados instancia;
```

📍 `singleton/BancoDeDados.java` · [linhas 35–40](https://github.com/aland3r/driftor-reuso/blob/7c48276/backend/src/driftor/singleton/BancoDeDados.java#L35-L40)

```java
    public static synchronized BancoDeDados getInstancia() {
        if (instancia == null) {
            instancia = new BancoDeDados();
        }
        return instancia;
    }
```

**5. Banco:** o mesmo objeto executa o SQL.

📍 `singleton/BancoDeDados.java` · [linhas 53–55](https://github.com/aland3r/driftor-reuso/blob/7c48276/backend/src/driftor/singleton/BancoDeDados.java#L53-L55)

```java
    public void executar(String sql, Object... parametros) {
        jdbc.update(sql, parametros);
    }
```

## Segundo exemplo

`Configuracao`, com as regras de cada papel e o endereço do motor: [`Configuracao.java:36`](https://github.com/aland3r/driftor-reuso/blob/7c48276/backend/src/driftor/singleton/Configuracao.java#L36). Todo controller chama `Configuracao.getInstancia().exigir(...)` ([variabilidade](../variabilidade.md)).
