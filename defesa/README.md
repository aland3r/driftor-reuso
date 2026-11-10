# Defesa: mapa rápido

Driftor (Reuso). Monólito em Python (FastAPI) com Postgres. Links fixos no commit `e88587c`.

| Tema | Arquivo |
|---|---|
| Os 4 CRUDs, operação por operação | [cruds.md](cruds.md) |
| Os 3 padrões de projeto, 2 exemplos de cada | [padroes-de-projeto.md](padroes-de-projeto.md) |
| A variabilidade (Gestor e Técnico) | [variabilidade.md](variabilidade.md) |
| As classes e as tabelas | [classes-e-tabelas.md](classes-e-tabelas.md) |
| Compactação de código (roteiro do vídeo) | [roteiro-video-compactacao.md](roteiro-video-compactacao.md) |

## Estrutura do código

```
backend/driftor/
  dominio.py            13 classes de domínio (regras)
  schema.sql            7 tabelas
  banco.py              BancoDeDados (Singleton)
  config.py             Configuracao (Singleton) + PAPEIS (variabilidade)
  telas.py              exigir(...) (variabilidade)
  acesso.py             entrada por perfil
  observador.py         Sujeito, Observador, AvisoNaTela (Observer)
  repositorio_base.py   RepositorioBase (compactação)
  mineracao/            grafo.py e detector.py (Adapters)
  processos/            CRUD Processo:   rotas.py + repositorio.py
  atividades/           CRUD Atividade:  rotas.py + repositorio.py
  analises/             CRUD Análise:    rotas.py + repositorio.py + eventos.py (Observer 1)
  manutencoes/          CRUD Manutenção: rotas.py + repositorio.py + eventos.py (Observer 2)
  main.py               monta o app e inscreve os observadores
frontend/               templates HTML e CSS
tests/                  testes
```

Caminho de toda operação: **botão → `rotas.py` → classe de `dominio.py` → `repositorio.py` (SQL) → `BancoDeDados` → Postgres.**

## Respostas curtas

| Pergunta | Resposta |
|---|---|
| Onde está o Create/Read/Update/Delete de X? | `backend/driftor/<x>/rotas.py` (comentários `# ---- Create`, `# ---- Read`…) e o SQL em `<x>/repositorio.py`. Tabela em [cruds.md](cruds.md). |
| Onde conecta no banco? | `BancoDeDados`, [`banco.py:20`](https://github.com/aland3r/driftor-reuso/blob/e88587c/backend/driftor/banco.py#L20) |
| Onde estão as tabelas? | [`schema.sql:5`](https://github.com/aland3r/driftor-reuso/blob/e88587c/backend/driftor/schema.sql#L5) |
| Onde estão as classes? | [`dominio.py:33`](https://github.com/aland3r/driftor-reuso/blob/e88587c/backend/driftor/dominio.py#L33) em diante |
| Singleton 1 e 2 | `Configuracao` [`config.py:29`](https://github.com/aland3r/driftor-reuso/blob/e88587c/backend/driftor/config.py#L29), `BancoDeDados` [`banco.py:20`](https://github.com/aland3r/driftor-reuso/blob/e88587c/backend/driftor/banco.py#L20) |
| Adapter 1 e 2 | `Pm4pyMineradorAdapter` [`grafo.py:25`](https://github.com/aland3r/driftor-reuso/blob/e88587c/backend/driftor/mineracao/grafo.py#L25), `RiverAdwinAdapter` [`detector.py:23`](https://github.com/aland3r/driftor-reuso/blob/e88587c/backend/driftor/mineracao/detector.py#L23) |
| Observer: base e inscrições | [`observador.py:14`](https://github.com/aland3r/driftor-reuso/blob/e88587c/backend/driftor/observador.py#L14), [`main.py:36`](https://github.com/aland3r/driftor-reuso/blob/e88587c/backend/driftor/main.py#L36) |
| Observer 1 e 2 | [`rotas.py:52`](https://github.com/aland3r/driftor-reuso/blob/e88587c/backend/driftor/analises/rotas.py#L52), [`rotas.py:32`](https://github.com/aland3r/driftor-reuso/blob/e88587c/backend/driftor/manutencoes/rotas.py#L32) |
| Variabilidade | `PAPEIS` [`config.py:13`](https://github.com/aland3r/driftor-reuso/blob/e88587c/backend/driftor/config.py#L13), `exigir` [`telas.py:49`](https://github.com/aland3r/driftor-reuso/blob/e88587c/backend/driftor/telas.py#L49) |
| Compactação | `RepositorioBase` [`repositorio_base.py:18`](https://github.com/aland3r/driftor-reuso/blob/e88587c/backend/driftor/repositorio_base.py#L18); antes `1f77872`, depois `c13a62b` |
| Testes | `tests/test_cruds.py` e `tests/test_fluxo_alfa.py` (9 testes) |
