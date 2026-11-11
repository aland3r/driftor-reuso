# CRUDs: do botão ao banco

[← voltar](../README.md) · links fixos no commit `82162ab`

## O caminho de uma operação

Exemplo: **editar uma atividade** (Update do CRUD de Atividade). Todas as outras operações seguem o mesmo caminho.

1. Na tela **Atividades**, o gestor muda o nome e clica em **Salvar**. O React chama a API com `PUT /api/atividades/{id}` e manda o papel no cabeçalho `Papel`: [`Atividades.jsx:19`](https://github.com/aland3r/driftor-reuso/blob/82162ab/frontend/src/telas/Atividades.jsx#L19)
2. O Spring entrega a chamada ao método `editar` do controller: [`AtividadeController.java:31`](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/atividade/AtividadeController.java#L31)
3. O controller confere se o papel pode mexer em atividades (variabilidade). Se não puder, para aqui com 403.
4. O repositório busca a atividade no banco (`select`, herdado de `RepositorioBase`).
5. A classe de domínio `Atividade` aplica a mudança no método `editar`: [`Atividade.java:20`](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/dominio/Atividade.java#L20)
6. O repositório grava com `update`: [`AtividadeRepositorio.java:29`](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/atividade/AtividadeRepositorio.java#L29)
7. O `BancoDeDados` (Singleton) executa o SQL no Postgres.
8. A tela recarrega a lista (`GET /api/atividades`).

📍 `atividade/AtividadeController.java` · linhas 30–37 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/atividade/AtividadeController.java#L30-L37)

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

📍 `atividade/AtividadeRepositorio.java` · linhas 27–31 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/atividade/AtividadeRepositorio.java#L27-L31)

```java
    // ---- Update
    public void atualizar(Atividade atividade) {
        banco.executar("update atividades set nome = ?, descricao = ? where id = ?",
                atividade.getNome(), atividade.getDescricao(), atividade.getId());
    }
```

## Onde está cada operação

Em cada controller e repositório, as operações estão marcadas com `// ---- Create`, `// ---- Read`, `// ---- Update` e `// ---- Delete`.

| CRUD | Create | Read | Update | Delete | Tela |
|---|---|---|---|---|---|
| Processo (Alander) | [`ProcessoController.java:31`](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/processo/ProcessoController.java#L31) | [`ProcessoController.java:24`](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/processo/ProcessoController.java#L24) | [`ProcessoController.java:60`](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/processo/ProcessoController.java#L60) | [`ProcessoController.java:69`](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/processo/ProcessoController.java#L69) | [`Processo.jsx:10`](https://github.com/aland3r/driftor-reuso/blob/82162ab/frontend/src/telas/Processo.jsx#L10) |
| Atividade (Alander) | [`AtividadeController.java:23`](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/atividade/AtividadeController.java#L23) | [`AtividadeController.java:16`](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/atividade/AtividadeController.java#L16) | [`AtividadeController.java:30`](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/atividade/AtividadeController.java#L30) | [`AtividadeController.java:39`](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/atividade/AtividadeController.java#L39) | [`Atividades.jsx:5`](https://github.com/aland3r/driftor-reuso/blob/82162ab/frontend/src/telas/Atividades.jsx#L5) |
| Análise (Emanuelle) | [`AnaliseController.java:23`](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/analise/AnaliseController.java#L23) | [`AnaliseController.java:39`](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/analise/AnaliseController.java#L39) | [`AnaliseController.java:48`](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/analise/AnaliseController.java#L48) | [`AnaliseController.java:57`](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/analise/AnaliseController.java#L57) | [`Analise.jsx:6`](https://github.com/aland3r/driftor-reuso/blob/82162ab/frontend/src/telas/Analise.jsx#L6) |
| Manutenção (Emanuelle) | [`ManutencaoController.java:24`](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/manutencao/ManutencaoController.java#L24) | [`ManutencaoController.java:17`](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/manutencao/ManutencaoController.java#L17) | [`ManutencaoController.java:41`](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/manutencao/ManutencaoController.java#L41) | [`ManutencaoController.java:51`](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/manutencao/ManutencaoController.java#L51) | [`Manutencoes.jsx:6`](https://github.com/aland3r/driftor-reuso/blob/82162ab/frontend/src/telas/Manutencoes.jsx#L6) |

O SQL de cada CRUD fica no repositório da mesma pasta (`ProcessoRepositorio`, `AtividadeRepositorio`, `AnaliseRepositorio`, `ManutencaoRepositorio`).

**Upload do log:** ao carregar o `.xes`, o processo grava os eventos e cria uma atividade para cada nome novo. Por isso as atividades e o grafo aparecem direto: [`ProcessoRepositorio.java:40`](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/processo/ProcessoRepositorio.java#L40)
