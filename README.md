# Driftor (Reuso)

Versão simplificada do Driftor para a disciplina de **Desenvolvimento Orientado a Reuso**. É um monólito em Python: o mesmo programa tem as telas (HTML com Jinja), as regras e o acesso ao banco (Postgres no Supabase, schema `driftor_reuso`). Não há login.

**Grupo:** Alander Menezes Arantes de Ávila e Emanuelle Skolut Jose.

## O que o produto faz

1. Cria um **processo** só com o nome.
2. Carrega o **log de eventos** (.xes ou .csv) na página do processo.
3. **Mapeia** cada operação do log para uma **atividade** do catálogo. Com isso, aparecem o grafo e as variantes.
4. Gera uma **análise de desvios** (ADWIN) sobre a duração de uma atividade e mostra onde o processo mudou.
5. Registra **notas** em cada desvio: o que aconteceu na máquina naquele trecho.

## Onde está cada item da avaliação

| Item | Onde |
|---|---|
| 13 classes principais com atributos e métodos | `driftor/dominio.py` |
| CRUD de Processo (Alander) | `driftor/processos/` (rotas + repositório) e `templates/processos/` |
| CRUD de Atividade (Alander) | `driftor/atividades/` e `templates/atividades/` |
| CRUD de Análise (Emanuelle) | `driftor/analises/` e `templates/analises/` |
| CRUD de Nota de drift (Emanuelle) | `driftor/notas/` e `templates/notas/` |
| 7 tabelas | `driftor/schema.sql` |
| Singleton 1: `Configuracao` | `driftor/config.py` |
| Singleton 2: `BancoDeDados` | `driftor/banco.py` |
| Adapter 1: `Pm4pyMineradorAdapter` → `MineradorDeGrafo` | `driftor/mineracao/grafo.py` |
| Adapter 2: `RiverAdwinAdapter` → `DetectorDeDrift` | `driftor/mineracao/detector.py` |
| Observer (base `Sujeito` e `Observador`) | `driftor/observador.py` |
| Observer 1: análise concluída | `driftor/analises/eventos.py` |
| Observer 2: nota criada ou excluída | `driftor/notas/eventos.py` |
| Inscrição dos observadores | `driftor/main.py` |
| Variabilidade: edições Essencial e Completa | `driftor/config.py` (`EDICOES`) e `driftor/telas.py` (`exigir_recurso`) |
| Compactação de código | `driftor/repositorio_base.py` e `templates/_componentes.html` (antes: commit `1f77872`, depois: `c13a62b`) |

## Variabilidade

O mesmo código gera dois produtos. A variável `EDICAO` escolhe a edição:

| Edição | Recursos |
|---|---|
| Essencial | Processos e Atividades |
| Completa | Processos, Atividades, Análises e Notas |

Na Essencial, o menu não mostra Análises e as rotas de análise e nota respondem 404.

## Rodar localmente

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env   # preencha DATABASE_URL
export $(cat .env | xargs)
uvicorn driftor.main:app --reload
```

As tabelas são criadas sozinhas na primeira vez que o app sobe. A pasta `exemplos/` tem os quatro logs sintéticos da Alfa. Com a série `Machine_Operating`, δ 0,002 e tratamento bruto, eles dão 0, 4, 7 e 9 desvios.

## Testes

```bash
pytest -q
```

Os testes precisam de um Postgres local com o schema `driftor_reuso` (o CI sobe um).
