# Roteiro do vídeo: compactação de código

Vídeo da equipe, não listado no YouTube. Duração alvo de 3 a 4 minutos. Mostrar a tela do GitHub ou do editor.

**Técnica:** extração do código repetido para uma superclasse genérica (`RepositorioBase`) e para macros de template (`_componentes.html`). Reuso por herança no Python e por importação de macros no Jinja.

- Antes: commit [`1f77872`](https://github.com/aland3r/driftor-reuso/tree/1f77872)
- Depois: commit [`c13a62b`](https://github.com/aland3r/driftor-reuso/tree/c13a62b)
- Diferença: [comparar os dois](https://github.com/aland3r/driftor-reuso/compare/1f77872...c13a62b)

## Passo 1: mostrar a repetição (commit antes)

> **Fala:** "No primeiro commit, os quatro repositórios (processos, atividades, análises e notas de drift, que depois virou o CRUD de manutenção) tinham o mesmo código para buscar um registro pelo id, listar e excluir. As quatro rotas também tinham uma função igual, `_xxx_ou_erro`, para dar erro quando o registro não existe."

Abrir lado a lado `driftor/atividades/repositorio.py` e `driftor/notas/repositorio.py` no commit `1f77872` (naquela época, o código ainda não estava dividido em `backend/` e `frontend/`). Apontar os métodos `obter` e `excluir`, que são iguais e só mudam o nome da tabela.

> **Fala:** "Nas telas, o botão vermelho de excluir com a confirmação estava copiado em sete lugares, o campo de renomear em dois, e a linha de "nada cadastrado" em seis."

## Passo 2: criar a superclasse

> **Fala:** "Criamos a classe `RepositorioBase`. Cada repositório só diz a sua tabela, as suas colunas e como transformar uma linha do banco em objeto. Listar, obter, obter-ou-erro e excluir são herdados."

📍 `backend/driftor/repositorio_base.py` · linhas 18–47 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/dfa0e7f/backend/driftor/repositorio_base.py#L18-L47)

```python
class RepositorioBase(Generic[T]):
    tabela: str = ""
    colunas: str = "*"
    ordem: str = "id"
    nome_no_singular: str = "registro"

    def __init__(self) -> None:
        self.banco = BancoDeDados()

    def criar_objeto(self, linha: dict) -> T:
        raise NotImplementedError

    # ---- Read
    def listar(self) -> list[T]:
        linhas = self.banco.consultar(f"select {self.colunas} from {self.tabela} order by {self.ordem}")
        return [self.criar_objeto(linha) for linha in linhas]

    def obter(self, id: str) -> T | None:
        linha = self.banco.consultar_um(f"select {self.colunas} from {self.tabela} where id = :id", id=id)
        return self.criar_objeto(linha) if linha else None

    def obter_ou_erro(self, id: str) -> T:
        objeto = self.obter(id)
        if objeto is None:
            raise ErroDeNegocio(f"{self.nome_no_singular.capitalize()} não encontrado(a).")
        return objeto

    # ---- Delete
    def excluir(self, id: str) -> None:
        self.banco.executar(f"delete from {self.tabela} where id = :id", id=id)
```

## Passo 3: cada repositório herda

> **Fala:** "O repositório de atividades agora só declara a tabela e as colunas. O `obter` e o `listar` sumiram daqui, porque vêm da base."

📍 `backend/driftor/atividades/repositorio.py` · linhas 11–19 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/dfa0e7f/backend/driftor/atividades/repositorio.py#L11-L19)

```python
class RepositorioDeAtividades(RepositorioBase[Atividade]):
    # listar, obter e obter_ou_erro vêm de RepositorioBase
    tabela = "atividades"
    colunas = "id, nome, descricao"
    ordem = "nome"
    nome_no_singular = "atividade"

    def criar_objeto(self, linha: dict) -> Atividade:
        return Atividade(id=str(linha["id"]), nome=linha["nome"], descricao=linha["descricao"])
```

## Passo 4: as macros de tela

> **Fala:** "O mesmo nas telas: o botão de excluir, o campo de renomear e a linha vazia viraram macros em `_componentes.html`. Cada tela importa e chama a macro numa linha."

📍 `frontend/templates/_componentes.html` · linhas 4–8 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/dfa0e7f/frontend/templates/_componentes.html#L4-L8)

```jinja
{% macro botao_excluir(url, pergunta, rotulo="Excluir") %}
<form class="inline" method="post" action="{{ url }}" onsubmit="return confirm({{ pergunta|tojson|forceescape }})">
  <button class="btn btn-sm">{{ rotulo }}</button>
</form>
{% endmacro %}
```

Mostrar uma tela usando a macro:

📍 `frontend/templates/atividades/lista.html` · linhas 23–23 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/dfa0e7f/frontend/templates/atividades/lista.html#L23-L23)

```jinja
        <td class="acoes"><a class="btn btn-sm" href="/atividades/{{ a.id }}/editar">Editar</a>{{ botao_excluir("/atividades/" ~ a.id ~ "/excluir", "Excluir a atividade " ~ a.nome ~ "?") }}</td>
```

## Passo 5: provar que nada quebrou

> **Fala:** "Rodamos os testes depois da compactação e todos continuam passando. A prova de que a técnica funciona veio depois: o CRUD de Manutenção foi criado já herdando de `RepositorioBase`, e o repositório dele só tem a tabela, as colunas e o SQL próprio."

📍 `backend/driftor/manutencoes/repositorio.py` · linhas 9–15 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/dfa0e7f/backend/driftor/manutencoes/repositorio.py#L9-L15)

```python
class RepositorioDeManutencoes(RepositorioBase[Manutencao]):
    # obter, obter_ou_erro e excluir vêm de RepositorioBase
    tabela = "manutencoes"
    colunas = "id, analise_id, drift_id, descricao, status, observacoes, criado_em, concluida_em"
    nome_no_singular = "manutenção"

    def criar_objeto(self, linha: dict) -> Manutencao:
```

Mostrar `pytest -q` passando, ou a aba Actions do GitHub verde.
