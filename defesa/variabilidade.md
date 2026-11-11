# Variabilidade por papel

[← voltar](../README.md) · links fixos no commit `3e19e1d`

O mesmo produto atende dois papéis: **Gestor** e **Técnico de manutenção**. A entrada é simulada, sem senha: a pessoa escolhe o papel, e toda chamada à API leva esse papel no cabeçalho `Papel`.

| | Gestor | Técnico |
|---|---|---|
| Tela inicial | Processos | Manutenções |
| Processo e Atividade | tudo | sem acesso (403) |
| Análise | tudo | só vê o detalhe |
| Manutenção | dispara e exclui | conclui |
| Avisos (Observer) | análise e manutenção concluídas | manutenção nova |

## 1. Onde a variação é definida

As permissões de cada papel ficam na `Configuracao`. Mudar o que um papel pode é mudar só este trecho.

📍 `singleton/Configuracao.java` · linhas 20–25 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/3e19e1d/backend/src/driftor/singleton/Configuracao.java#L20-L25)

```java
    /** VARIABILIDADE por papel: o que cada perfil pode fazer no mesmo produto. */
    private final Map<String, Papel> papeis = Map.of(
            "gestor", new Papel("Gestor", "/processos",
                    Set.of("processos", "atividades", "analises", "ver_analise", "manutencoes", "disparar_manutencao")),
            "tecnico", new Papel("Técnico de manutenção", "/manutencoes",
                    Set.of("manutencoes", "ver_analise", "concluir_manutencao")));
```

## 2. Onde a variação é aplicada

No back-end, cada operação chama `exigir` antes de fazer qualquer coisa:

📍 `singleton/Configuracao.java` · linhas 43–47 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/3e19e1d/backend/src/driftor/singleton/Configuracao.java#L43-L47)

```java
    public void exigir(String papel, String permissao) {
        if (!papeis.containsKey(papel) || !papeis.get(papel).pode().contains(permissao)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Este perfil não tem acesso.");
        }
    }
```

Exemplo: [`ManutencaoController.java:44`](https://github.com/aland3r/driftor-reuso/blob/3e19e1d/backend/src/driftor/manutencao/ManutencaoController.java#L44)

No front, o menu mostra só o que o papel pode usar: [`main.jsx:29`](https://github.com/aland3r/driftor-reuso/blob/3e19e1d/frontend/src/main.jsx#L29). Os botões de gestor só aparecem para ele: [`Analise.jsx:15`](https://github.com/aland3r/driftor-reuso/blob/3e19e1d/frontend/src/telas/Analise.jsx#L15)
