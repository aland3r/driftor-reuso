# Variabilidade

Links fixos no commit `dfa0e7f`.

**Exemplo escolhido: variabilidade por papel.** O mesmo código atende dois perfis, Gestor e Técnico de manutenção. A entrada é simulada (sem senha): a pessoa escolhe o perfil, o papel vai para um cookie, e cada rota confere se aquele papel tem a permissão que ela exige.

| | Gestor | Técnico de manutenção |
|---|---|---|
| Começa em | `/processos` | `/manutencoes` |
| Processo e Atividade | tudo | sem acesso (403) |
| Análise | tudo | só o detalhe |
| Manutenção | dispara, edita, exclui | conclui |
| Avisos | análise e manutenção concluídas | manutenção nova |

## 1. Onde a variação é definida

O dicionário `PAPEIS` lista as permissões de cada papel. Mudar o que um papel pode é mudar só este dicionário.

📍 `backend/driftor/config.py` · linhas 13–26 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/dfa0e7f/backend/driftor/config.py#L13-L26)

```python
PAPEIS = {
    "gestor": {
        "nome": "Gestor",
        "descricao": "Mapeia os processos, gera as análises de desvio e dispara as manutenções.",
        "inicio": "/processos",
        "pode": {"processos", "atividades", "analises", "ver_analise", "manutencoes", "disparar_manutencao"},
    },
    "tecnico": {
        "nome": "Técnico de manutenção",
        "descricao": "Recebe as manutenções disparadas, executa e registra as observações.",
        "inicio": "/manutencoes",
        "pode": {"manutencoes", "ver_analise", "concluir_manutencao"},
    },
}
```

A pergunta "este papel tem esta permissão?" fica no Singleton `Configuracao`:

📍 `backend/driftor/config.py` · linhas 45–47 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/dfa0e7f/backend/driftor/config.py#L45-L47)

```python
    def pode(self, papel: str | None, permissao: str) -> bool:
        """Pergunta da variabilidade: este papel tem esta permissão?"""
        return papel in self.papeis and permissao in self.papeis[papel]["pode"]
```

## 2. Onde o papel é escolhido

📍 `backend/driftor/acesso.py` · linhas 28–34 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/dfa0e7f/backend/driftor/acesso.py#L28-L34)

```python
@rotas.post("/entrar")
def entrar(papel: str = Form("")):
    if papel not in PAPEIS:
        raise ErroDeNegocio("Escolha um perfil.")
    resposta = ir_para(PAPEIS[papel]["inicio"])
    resposta.set_cookie("papel", papel, httponly=True, samesite="lax")
    return resposta
```

📍 `backend/driftor/telas.py` · linhas 28–30 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/dfa0e7f/backend/driftor/telas.py#L28-L30)

```python
def papel_atual(request: Request) -> str | None:
    papel = request.cookies.get("papel")
    return papel if papel in PAPEIS else None
```

## 3. Onde a variação é aplicada

A função `exigir` vira uma dependência da rota. Sem papel, manda para a entrada; com um papel sem permissão, devolve 403.

📍 `backend/driftor/telas.py` · linhas 49–60 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/dfa0e7f/backend/driftor/telas.py#L49-L60)

```python
def exigir(permissao: str):
    """VARIABILIDADE: a rota só abre se o papel de quem entrou tem a permissão."""

    def verificar(request: Request) -> str:
        papel = papel_atual(request)
        if papel is None:
            raise PrecisaEntrar()
        if not Configuracao().pode(papel, permissao):
            raise SemPermissao(permissao)
        return papel

    return verificar
```

Uso nas rotas:

| Onde | Permissão |
|---|---|
| [`rotas.py:15`](https://github.com/aland3r/driftor-reuso/blob/dfa0e7f/backend/driftor/processos/rotas.py#L15) | `processos`, no roteador inteiro |
| [`rotas.py:11`](https://github.com/aland3r/driftor-reuso/blob/dfa0e7f/backend/driftor/atividades/rotas.py#L11) | `atividades`, no roteador inteiro |
| [`rotas.py:16`](https://github.com/aland3r/driftor-reuso/blob/dfa0e7f/backend/driftor/analises/rotas.py#L16) | `analises` (lista, criar, renomear, excluir) |
| [`rotas.py:60`](https://github.com/aland3r/driftor-reuso/blob/dfa0e7f/backend/driftor/analises/rotas.py#L60) | `ver_analise` (detalhe) |
| [`rotas.py:27`](https://github.com/aland3r/driftor-reuso/blob/dfa0e7f/backend/driftor/manutencoes/rotas.py#L27) | `disparar_manutencao` (criar, editar, excluir) |
| [`rotas.py:48`](https://github.com/aland3r/driftor-reuso/blob/dfa0e7f/backend/driftor/manutencoes/rotas.py#L48) | `concluir_manutencao` (concluir) |

A resposta 403:

📍 `backend/driftor/main.py` · linhas 67–71 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/dfa0e7f/backend/driftor/main.py#L67-L71)

```python
@app.exception_handler(SemPermissao)
def sem_permissao(request: Request, _erro: SemPermissao):
    resposta = tela(request, "erro.html", mensagem="Este perfil não tem acesso a esta tela.", voltar="/")
    resposta.status_code = 403
    return resposta
```

## 4. A variação também aparece no Observer

Cada papel tem a sua caixa de avisos, e cada caixa só aceita os eventos do papel:

📍 `backend/driftor/observador.py` · linhas 55–58 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/dfa0e7f/backend/driftor/observador.py#L55-L58)

```python
avisos_por_papel = {
    "gestor": AvisoNaTela({"analise_concluida", "manutencao_concluida"}),
    "tecnico": AvisoNaTela({"manutencao_disparada"}),
}
```

## 5. Teste que prova

📍 `tests/test_cruds.py` · linhas 71–85 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/dfa0e7f/tests/test_cruds.py#L71-L85)

```python
def test_variabilidade_por_papel(cliente):
    _analise_com_um_desvio()
    entrar(cliente, "tecnico")
    menu = cliente.get("/manutencoes").text
    assert 'href="/processos"' not in menu and 'href="/manutencoes"' in menu
    assert cliente.get("/processos").status_code == 403
    assert cliente.get("/analises").status_code == 403
    assert cliente.post(f"/analises/{ANALISE}/manutencoes", data={"drift_id": DRIFT, "descricao": "x"}).status_code == 403
    analise = cliente.get(f"/analises/{ANALISE}")  # o técnico vê a análise de origem, sem editar
    assert analise.status_code == 200 and "Renomear" not in analise.text and "Disparar manutenção" not in analise.text

    entrar(cliente, "gestor")
    assert cliente.get("/processos").status_code == 200
    assert "Disparar manutenção" in cliente.get(f"/analises/{ANALISE}").text

```
