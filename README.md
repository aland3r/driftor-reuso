# Driftor (Reuso)

**🌐 Site em produção: [driftor-reuso.fly.dev](https://driftor-reuso.fly.dev)**. Entre como Gestor ou Técnico de manutenção, sem senha. Cada commit na `main` publica uma nova versão.

**Grupo:** Alander Menezes Arantes de Ávila e Emanuelle Skolut Jose.

## Como funciona

- **Backend em Java (Spring Boot)**, em `backend/`: as classes, os padrões, os CRUDs e o SQL.
- **Front em React**, em `frontend/`: as telas chamam a API do backend.
- **Postgres** no Supabase, schema `driftor_reuso`, com 6 tabelas.
- **Motor de mineração em Python**, em `motor/`: lê o log, descobre o grafo (PM4Py) e detecta os desvios (ADWIN). Não faz parte do que defendemos; o backend só chama esse motor pelos Adapters.

O fluxo: o gestor cria um processo e sobe o log `.xes`. As atividades e o grafo aparecem direto. Ele gera a análise de desvios e dispara uma manutenção a partir de um desvio. O técnico recebe o aviso, executa e conclui.

## Defesa

Tudo em [`docs/`](docs/README.md): os [4 CRUDs](docs/cruds/README.md), os [padrões](docs/padroes/) ([Singleton](docs/padroes/singleton.md) · [Adapter](docs/padroes/adapter.md) · [Observer](docs/padroes/observer.md)), a [variabilidade](docs/variabilidade.md), a [compactação](docs/compactacao.md) e as [classes e tabelas](docs/classes-e-tabelas.md). Cada arquivo mostra o caminho completo, da tela até o banco.

## Onde está cada item do enunciado

| Item | Onde |
|---|---|
| 12 classes com atributos e métodos | pasta [`dominio/`](https://github.com/aland3r/driftor-reuso/tree/7c48276/backend/src/driftor/dominio) · [lista](docs/classes-e-tabelas.md) |
| 3 padrões, 2 exemplos de cada | [Singleton](docs/padroes/singleton.md) · [Adapter](docs/padroes/adapter.md) · [Observer](docs/padroes/observer.md) |
| 4 CRUDs com banco (Processo, Atividade, Análise, Manutenção) | [cruds/](docs/cruds/README.md) |
| 3 tabelas ou mais | [schema.sql](https://github.com/aland3r/driftor-reuso/blob/7c48276/backend/src/schema.sql) (6 tabelas) |
| Variabilidade | [variabilidade.md](docs/variabilidade.md) |
| Compactação de código | [compactacao.md](docs/compactacao.md) |
