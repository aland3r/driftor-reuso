# CRUDs

[← defesa](../README.md) · links fixos no commit `21ee145`

Cada arquivo mostra as 4 operações de um CRUD, da tela até o SQL.

| CRUD | Tela | Controller | Repositório (SQL) | Classe |
|---|---|---|---|---|
| [Processo](processo.md) | `Processos.jsx`, `Processo.jsx` | `ProcessoController` | `ProcessoRepositorio` | `Processo` |
| [Atividade](atividade.md) | `Atividades.jsx` | `AtividadeController` | `AtividadeRepositorio` | `Atividade` |
| [Análise](analise.md) | `Processo.jsx`, `Analise.jsx` | `AnaliseController` | `AnaliseRepositorio` | `Analise` |
| [Manutenção](manutencao.md) | `Analise.jsx`, `Manutencoes.jsx`, `Manutencao.jsx` | `ManutencaoController` | `ManutencaoRepositorio` | `Manutencao` |

## O caminho, igual em todas as operações

1. **Tela (React):** o botão chama a função `api`, que faz a requisição HTTP e manda o papel no cabeçalho `Papel`.
2. **Controller (Java):** o Spring entrega a requisição ao método certo. Ele confere o papel (variabilidade) e usa o domínio e o repositório.
3. **Domínio:** a classe aplica a regra (criar, renomear, concluir...).
4. **Repositório:** monta o SQL e chama o `BancoDeDados` (Singleton), que executa no Postgres.

A função `api`, usada por todas as telas:

📍 `frontend/src/api.js` · linhas 4–14 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/21ee145/frontend/src/api.js#L4-L14)

```js
export async function api(metodo, url, corpo) {
  const opcoes = { method: metodo, headers: { Papel: papel() } };
  if (corpo instanceof FormData) opcoes.body = corpo;
  else if (corpo) {
    opcoes.headers["Content-Type"] = "application/json";
    opcoes.body = JSON.stringify(corpo);
  }
  const resposta = await fetch("/api" + url, opcoes);
  const texto = await resposta.text();
  return texto ? JSON.parse(texto) : null;
}
```
