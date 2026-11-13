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

Tudo em [`defesa/`](defesa/README.md): os [4 CRUDs](defesa/cruds/README.md), os [padrões](defesa/padroes/) ([Singleton](defesa/padroes/singleton.md) · [Adapter](defesa/padroes/adapter.md) · [Observer](defesa/padroes/observer.md)), a [variabilidade](defesa/variabilidade.md), a [compactação](defesa/compactacao.md) e as [classes e tabelas](defesa/classes-e-tabelas.md). Cada arquivo mostra o caminho completo, da tela até o banco.

## Onde está cada item do enunciado

| Item | Onde |
|---|---|
| 12 classes com atributos e métodos | pasta [`dominio/`](https://github.com/aland3r/driftor-reuso/tree/e17947a/backend/src/driftor/dominio) · [lista](defesa/classes-e-tabelas.md) |
| 3 padrões, 2 exemplos de cada | [Singleton](defesa/padroes/singleton.md) · [Adapter](defesa/padroes/adapter.md) · [Observer](defesa/padroes/observer.md) |
| 4 CRUDs com banco (Processo, Atividade, Análise, Manutenção) | [cruds/](defesa/cruds/README.md) |
| 3 tabelas ou mais | [schema.sql](https://github.com/aland3r/driftor-reuso/blob/e17947a/backend/src/schema.sql) (6 tabelas) |
| Variabilidade | [variabilidade.md](defesa/variabilidade.md) |
| Compactação de código | [compactacao.md](defesa/compactacao.md) |
