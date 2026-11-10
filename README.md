# Driftor (Reuso)

Versão simplificada do Driftor para a disciplina de **Desenvolvimento Orientado a Reuso**. É um monólito em Python: o mesmo programa tem as telas (HTML com Jinja), as regras e o acesso ao banco (Postgres no Supabase, schema `driftor_reuso`). Não há login de verdade: a entrada só escolhe o perfil (Gestor ou Técnico de manutenção).

**Grupo:** Alander Menezes Arantes de Ávila e Emanuelle Skolut Jose.

**Divisão dos CRUDs:** Alander, Processo e Atividade; Emanuelle, Análise e Manutenção. Os dois respondem por todos.

**Defesa:** o mapa por tema está em [`defesa/README.md`](defesa/README.md).

## O que o produto faz

1. Cria um **processo** só com o nome.
2. Carrega o **log de eventos** (.xes ou .csv) na página do processo.
3. **Mapeia** cada operação do log para uma **atividade** do catálogo. Com isso, aparecem o grafo e as variantes.
4. Gera uma **análise de desvios** (ADWIN) sobre a duração de uma atividade e mostra onde o processo mudou.
5. O gestor **dispara uma manutenção** a partir de um desvio da análise.
6. O técnico vê a manutenção notificada, executa e marca como **concluída** com as observações.

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `backend/driftor/` | back-end: domínio (`dominio.py`), um pacote por CRUD (`rotas.py` + `repositorio.py`), banco, padrões de projeto |
| `frontend/` | front-end: `templates/` (HTML com Jinja) e `static/` (CSS) |
| `tests/` | testes dos CRUDs, do fluxo gestor → técnico e da variabilidade |
| `exemplos/` | os quatro logs sintéticos da Alfa |
| `defesa/` | material da defesa, por tema (CRUDs, padrões, variabilidade, classes e tabelas, compactação) |

## Onde está cada item da avaliação

| Item | Onde |
|---|---|
| 13 classes principais com atributos e métodos | `backend/driftor/dominio.py` |
| CRUD de Processo | `backend/driftor/processos/` (rotas + repositório) e `frontend/templates/processos/` |
| CRUD de Atividade | `backend/driftor/atividades/` e `frontend/templates/atividades/` |
| CRUD de Análise | `backend/driftor/analises/` e `frontend/templates/analises/` |
| CRUD de Manutenção | `backend/driftor/manutencoes/` e `frontend/templates/manutencoes/` |
| 7 tabelas | `backend/driftor/schema.sql` |
| Singleton 1: `Configuracao` | `backend/driftor/config.py` |
| Singleton 2: `BancoDeDados` | `backend/driftor/banco.py` |
| Adapter 1: `Pm4pyMineradorAdapter` → `MineradorDeGrafo` | `backend/driftor/mineracao/grafo.py` |
| Adapter 2: `RiverAdwinAdapter` → `DetectorDeDrift` | `backend/driftor/mineracao/detector.py` |
| Observer (base `Sujeito` e `Observador`) | `backend/driftor/observador.py` |
| Observer 1: análise concluída | `backend/driftor/analises/eventos.py` |
| Observer 2: manutenção disparada ou concluída | `backend/driftor/manutencoes/eventos.py` |
| Inscrição dos observadores | `backend/driftor/main.py` |
| Variabilidade por perfil: Gestor e Técnico | `backend/driftor/config.py` (`PAPEIS`), `backend/driftor/telas.py` (`exigir`) e `backend/driftor/acesso.py` |
| Compactação de código | `backend/driftor/repositorio_base.py` e `frontend/templates/_componentes.html` (antes: commit `1f77872`, depois: `c13a62b`) |

## Variabilidade

O mesmo código atende dois perfis. Na entrada, a pessoa escolhe o perfil, e `Configuracao().pode(papel, permissao)` decide o que ela vê e faz:

| Perfil | Começa em | Pode |
|---|---|---|
| Gestor | Processos | processos, atividades, análises e disparar, editar e excluir manutenções |
| Técnico de manutenção | Manutenções | ver as manutenções e a análise de origem, e concluir com observações |

O menu só mostra o que o perfil pode. Se o técnico abrir uma tela do gestor pelo endereço, recebe 403.

## Rodar localmente

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env   # preencha DATABASE_URL
export $(cat .env | xargs)
PYTHONPATH=backend uvicorn driftor.main:app --reload
```

As tabelas são criadas sozinhas na primeira vez que o app sobe. A pasta `exemplos/` tem os quatro logs sintéticos da Alfa. Com a série `Machine_Operating`, δ 0,002 e tratamento bruto, eles dão 0, 4, 7 e 9 desvios.

## Testes

```bash
pytest -q
```

Os testes precisam de um Postgres local com o schema `driftor_reuso` (o CI sobe um).
