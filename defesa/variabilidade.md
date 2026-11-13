# Variabilidade por papel

[← defesa](README.md) · links fixos no commit `e17947a`

O mesmo produto atende dois papéis: **Gestor** e **Técnico de manutenção**. A entrada é simulada, sem senha: a pessoa escolhe o papel, e toda chamada à API leva esse papel no cabeçalho `Papel`.

| | Gestor | Técnico |
|---|---|---|
| Tela inicial | Processos | Manutenções |
| Processo e Atividade | tudo | sem acesso (403) |
| Análise | tudo | só vê o detalhe |
| Manutenção | dispara e exclui | conclui |
| Avisos (Observer) | análise e manutenção concluídas | manutenção nova |

## 1. Tela de entrada: o papel é escolhido

O papel escolhido fica guardado no navegador:

📍 `frontend/src/telas/Entrar.jsx` · [linhas 12–12](https://github.com/aland3r/driftor-reuso/blob/e17947a/frontend/src/telas/Entrar.jsx#L12-L12)

```jsx
  const entrar = (chave) => { localStorage.setItem("papel", chave); navegar(papeis[chave].inicio); };
```

Toda chamada à API leva esse papel no cabeçalho `Papel`:

📍 `frontend/src/api.js` · [linhas 2–5](https://github.com/aland3r/driftor-reuso/blob/e17947a/frontend/src/api.js#L2-L5)

```js
export const papel = () => localStorage.getItem("papel");

export async function api(metodo, url, corpo) {
  const opcoes = { method: metodo, headers: { Papel: papel() } };
```

## 2. Onde a variação é definida

As permissões de cada papel ficam na `Configuracao`. Mudar o que um papel pode é mudar só este trecho.

📍 `singleton/Configuracao.java` · [linhas 20–25](https://github.com/aland3r/driftor-reuso/blob/e17947a/backend/src/driftor/singleton/Configuracao.java#L20-L25)

```java
    /** VARIABILIDADE por papel: o que cada perfil pode fazer no mesmo produto. */
    private final Map<String, Papel> papeis = Map.of(
            "gestor", new Papel("Gestor", "/processos",
                    Set.of("processos", "atividades", "analises", "ver_analise", "manutencoes", "disparar_manutencao")),
            "tecnico", new Papel("Técnico de manutenção", "/manutencoes",
                    Set.of("manutencoes", "ver_analise", "concluir_manutencao")));
```

## 3. Onde a variação é aplicada

No back-end, cada operação chama `exigir` antes de fazer qualquer coisa:

📍 `singleton/Configuracao.java` · [linhas 44–48](https://github.com/aland3r/driftor-reuso/blob/e17947a/backend/src/driftor/singleton/Configuracao.java#L44-L48)

```java
    public void exigir(String papel, String permissao) {
        if (!papeis.containsKey(papel) || !papeis.get(papel).pode().contains(permissao)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Este perfil não tem acesso.");
        }
    }
```

Exemplo: [`ManutencaoController.java:44`](https://github.com/aland3r/driftor-reuso/blob/e17947a/backend/src/driftor/manutencao/ManutencaoController.java#L44)

No front, o menu mostra só o que o papel pode usar: [`main.jsx:32`](https://github.com/aland3r/driftor-reuso/blob/e17947a/frontend/src/main.jsx#L32). Os botões de gestor só aparecem para ele: [`Analise.jsx:16`](https://github.com/aland3r/driftor-reuso/blob/e17947a/frontend/src/telas/Analise.jsx#L16)
