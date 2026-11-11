# Classes e tabelas

[← voltar](../README.md) · links fixos no commit `3e19e1d`

## As 12 classes de domínio

Todas na pasta `dominio/`. Cada nome abre a classe.

| Classe | Atributos | Métodos |
|---|---|---|
| [`Processo.java:6`](https://github.com/aland3r/driftor-reuso/blob/3e19e1d/backend/src/driftor/dominio/Processo.java#L6) | id, nome, arquivo, totalTraces, totalEventos | `criar`, `renomear`, `carregarLog` |
| [`Evento.java:5`](https://github.com/aland3r/driftor-reuso/blob/3e19e1d/backend/src/driftor/dominio/Evento.java#L5) | atividade, inicio, duracao | `eDaAtividade` |
| [`Trace.java:8`](https://github.com/aland3r/driftor-reuso/blob/3e19e1d/backend/src/driftor/dominio/Trace.java#L8) | caseId, eventos | `adicionar`, `inicio`, `sequencia`, `duracao` |
| [`Atividade.java:5`](https://github.com/aland3r/driftor-reuso/blob/3e19e1d/backend/src/driftor/dominio/Atividade.java#L5) | id, nome, descricao | `criar`, `editar` |
| [`Variante.java:9`](https://github.com/aland3r/driftor-reuso/blob/3e19e1d/backend/src/driftor/dominio/Variante.java#L9) | numero, sequencia, totalTraces | `agrupar`, `getDescricao` |
| [`No.java:4`](https://github.com/aland3r/driftor-reuso/blob/3e19e1d/backend/src/driftor/dominio/No.java#L4) | atividade, frequencia | `rotulo` |
| [`Aresta.java:4`](https://github.com/aland3r/driftor-reuso/blob/3e19e1d/backend/src/driftor/dominio/Aresta.java#L4) | origem, destino, frequencia | (só dados) |
| [`Grafo.java:9`](https://github.com/aland3r/driftor-reuso/blob/3e19e1d/backend/src/driftor/dominio/Grafo.java#L9) | nos, arestas | `montar`, `paraMermaid` |
| [`PontoDaSerie.java:8`](https://github.com/aland3r/driftor-reuso/blob/3e19e1d/backend/src/driftor/dominio/PontoDaSerie.java#L8) | posicao, caseId, valor | `serieDeDuracao` |
| [`Drift.java:6`](https://github.com/aland3r/driftor-reuso/blob/3e19e1d/backend/src/driftor/dominio/Drift.java#L6) | id, posicao, inicio, mediaAntes, mediaDepois | `variacaoPct`, `getResumo` |
| [`Analise.java:8`](https://github.com/aland3r/driftor-reuso/blob/3e19e1d/backend/src/driftor/dominio/Analise.java#L8) | id, processoId, nome, atividade, delta, totalObservacoes, drifts | `criar`, `renomear`, `registrarResultado` |
| [`Manutencao.java:6`](https://github.com/aland3r/driftor-reuso/blob/3e19e1d/backend/src/driftor/dominio/Manutencao.java#L6) | id, analiseId, driftId, descricao, status, observacoes | `disparar`, `estaPendente`, `concluir` |

## As 6 tabelas

Arquivo `schema.sql`. O backend executa esse arquivo ao subir (`BancoDeDados.criarTabelas`).

| Tabela | CRUD | Ligada a |
|---|---|---|
| [`schema.sql:3`](https://github.com/aland3r/driftor-reuso/blob/3e19e1d/backend/src/schema.sql#L3) | Processo | |
| [`schema.sql:11`](https://github.com/aland3r/driftor-reuso/blob/3e19e1d/backend/src/schema.sql#L11) | Atividade | |
| [`schema.sql:17`](https://github.com/aland3r/driftor-reuso/blob/3e19e1d/backend/src/schema.sql#L17) | Processo (o log) | processos, atividades |
| [`schema.sql:27`](https://github.com/aland3r/driftor-reuso/blob/3e19e1d/backend/src/schema.sql#L27) | Análise | processos |
| [`schema.sql:37`](https://github.com/aland3r/driftor-reuso/blob/3e19e1d/backend/src/schema.sql#L37) | Análise | analises |
| [`schema.sql:46`](https://github.com/aland3r/driftor-reuso/blob/3e19e1d/backend/src/schema.sql#L46) | Manutenção | analises, drifts |
