# Classes e tabelas

[← defesa](README.md) · links fixos no commit `21ee145`

## As 12 classes de domínio

Todas na pasta `dominio/`. Cada nome abre a classe.

| Classe | Atributos | Métodos |
|---|---|---|
| [`Processo.java:6`](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/dominio/Processo.java#L6) | id, nome, arquivo, totalTraces, totalEventos | `criar`, `renomear`, `carregarLog` |
| [`Evento.java:5`](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/dominio/Evento.java#L5) | atividade, inicio, duracao | `eDaAtividade` |
| [`Trace.java:8`](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/dominio/Trace.java#L8) | caseId, eventos | `adicionar`, `inicio`, `sequencia`, `duracao` |
| [`Atividade.java:5`](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/dominio/Atividade.java#L5) | id, nome | `criar`, `renomear` |
| [`Variante.java:9`](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/dominio/Variante.java#L9) | numero, sequencia, totalTraces | `agrupar`, `getDescricao` |
| [`No.java:4`](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/dominio/No.java#L4) | atividade, frequencia | `rotulo` |
| [`Aresta.java:4`](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/dominio/Aresta.java#L4) | origem, destino, frequencia | (só dados) |
| [`Grafo.java:9`](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/dominio/Grafo.java#L9) | nos, arestas | `montar`, `paraMermaid` |
| [`PontoDaSerie.java:8`](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/dominio/PontoDaSerie.java#L8) | posicao, caseId, valor | `serieDeDuracao` |
| [`Drift.java:6`](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/dominio/Drift.java#L6) | id, posicao, inicio, mediaAntes, mediaDepois | `variacaoPct`, `getResumo` |
| [`Analise.java:8`](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/dominio/Analise.java#L8) | id, processoId, nome, atividade, delta, totalObservacoes, drifts | `criar`, `renomear`, `registrarResultado` |
| [`Manutencao.java:6`](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/dominio/Manutencao.java#L6) | id, analiseId, driftId, descricao, status, observacoes | `disparar`, `estaPendente`, `concluir` |

## As 6 tabelas

Arquivo `schema.sql`. O backend executa esse arquivo ao subir (`BancoDeDados.criarTabelas`).

| Tabela | CRUD | Ligada a |
|---|---|---|
| [`schema.sql:3`](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/schema.sql#L3) | Processo | |
| [`schema.sql:11`](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/schema.sql#L11) | Atividade | |
| [`schema.sql:16`](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/schema.sql#L16) | Processo (o log) | processos, atividades |
| [`schema.sql:26`](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/schema.sql#L26) | Análise | processos |
| [`schema.sql:36`](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/schema.sql#L36) | Análise | analises |
| [`schema.sql:45`](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/schema.sql#L45) | Manutenção | analises, drifts |
