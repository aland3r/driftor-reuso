# Driftor (Reuso)

**🌐 Site em produção: [driftor-reuso.fly.dev](https://driftor-reuso.fly.dev)**. Entre como Gestor ou Técnico de manutenção, sem senha. Cada commit na `main` publica uma nova versão.

**Grupo:** Alander Menezes Arantes de Ávila e Emanuelle Skolut Jose.
**CRUDs:** Alander, Processo e Atividade; Emanuelle, Análise e Manutenção. Os dois respondem por todos.

## Como funciona

- **Backend em Java (Spring Boot)**, em `backend/`: as classes, os padrões, os CRUDs e o SQL.
- **Front em React**, em `frontend/`: as telas chamam a API do backend.
- **Postgres** no Supabase, schema `driftor_reuso`, com 6 tabelas.
- **Motor de mineração em Python**, em `motor/`: lê o log, descobre o grafo (PM4Py) e detecta os desvios (ADWIN). Não faz parte do que defendemos; o backend só chama esse motor pelos Adapters.

O fluxo: o gestor cria um processo e sobe o log `.xes`. As atividades e o grafo aparecem direto. Ele gera a análise de desvios e dispara uma manutenção a partir de um desvio. O técnico recebe o aviso, executa e conclui.

## Defesa

| Tema | Explicação |
|---|---|
| Caminho de um CRUD, do botão ao banco | [defesa/cruds.md](defesa/cruds.md) |
| Singleton | [defesa/singleton.md](defesa/singleton.md) |
| Adapter | [defesa/adapter.md](defesa/adapter.md) |
| Observer | [defesa/observer.md](defesa/observer.md) |
| Variabilidade por papel | [defesa/variabilidade.md](defesa/variabilidade.md) |
| Compactação de código (roteiro do vídeo) | [defesa/compactacao.md](defesa/compactacao.md) |
| As 12 classes e as 6 tabelas | [defesa/classes-e-tabelas.md](defesa/classes-e-tabelas.md) |

## Onde está cada item do enunciado

| Item | Onde |
|---|---|
| 12 classes com atributos e métodos | pasta [`dominio/`](https://github.com/aland3r/driftor-reuso/tree/f10116b/backend/src/driftor/dominio) · [lista](defesa/classes-e-tabelas.md) |
| 3 padrões, 2 exemplos de cada | [Singleton](defesa/singleton.md) · [Adapter](defesa/adapter.md) · [Observer](defesa/observer.md) |
| 2 CRUDs por integrante, com banco | [cruds.md](defesa/cruds.md) |
| 3 tabelas ou mais | [schema.sql](https://github.com/aland3r/driftor-reuso/blob/f10116b/backend/src/schema.sql) (6 tabelas) |
| Variabilidade | [variabilidade.md](defesa/variabilidade.md) |
| Compactação de código | [compactacao.md](defesa/compactacao.md) |
