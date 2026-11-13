# Observer

[← docs](../README.md) · links fixos no commit `7c48276`

**O que é:** um mecanismo de **assinatura**. Vários objetos se inscrevem para ser avisados quando algo acontece em outro.

**Partes:** **Subject** (guarda os inscritos, tem `inscrever` e `notificar`), **Observer** (interface com `atualizar`) e o **observador concreto** (o que cada inscrito faz).

**Por que usamos:** quem publica o evento (o controller) não sabe quem quer ser avisado. Para acrescentar uma reação, basta inscrever outro observador.

## Exemplo: manutenção disparada avisa o técnico

**1. Inscrição:** ao subir o app, a caixa de avisos do técnico se inscreve no Subject `MANUTENCAO`.

📍 `observer/Avisos.java` · [linhas 13–13](https://github.com/aland3r/driftor-reuso/blob/7c48276/backend/src/driftor/observer/Avisos.java#L13-L13)

```java
    public static final Subject MANUTENCAO = new Subject();
```

📍 `observer/Avisos.java` · [linhas 20–24](https://github.com/aland3r/driftor-reuso/blob/7c48276/backend/src/driftor/observer/Avisos.java#L20-L24)

```java
    public static void inscrever() {
        ANALISE.inscrever(CAIXA_DO_PAPEL.get("gestor"));
        MANUTENCAO.inscrever(CAIXA_DO_PAPEL.get("tecnico"));
        MANUTENCAO.inscrever(CAIXA_DO_PAPEL.get("gestor"));
    }
```

**2. Tela do gestor:** o botão **Disparar manutenção** chama a API.

📍 `frontend/src/telas/Analise.jsx` · [linhas 20–24](https://github.com/aland3r/driftor-reuso/blob/7c48276/frontend/src/telas/Analise.jsx#L20-L24)

```jsx
  const disparar = async (driftId) => {
    await api("POST", `/analises/${id}/manutencoes`, { driftId, descricao });
    setDescricao("");
    carregar();
  };
```

**3. Controller:** grava e publica o evento.

📍 `manutencao/ManutencaoController.java` · [linhas 24–31](https://github.com/aland3r/driftor-reuso/blob/7c48276/backend/src/driftor/manutencao/ManutencaoController.java#L24-L31)

```java
    // ---- Create: o gestor dispara a partir de um desvio
    @PostMapping("/api/analises/{analiseId}/manutencoes")
    public void disparar(@RequestHeader("Papel") String papel, @PathVariable UUID analiseId, @RequestBody Map<String, String> corpo) {
        Configuracao.getInstancia().exigir(papel, "disparar_manutencao");
        Manutencao manutencao = Manutencao.disparar(analiseId, UUID.fromString(corpo.get("driftId")), corpo.get("descricao"));
        repositorio.inserir(manutencao);
        Avisos.MANUTENCAO.notificar("manutencao_disparada", "Nova manutenção: " + manutencao.getDescricao());  // Observer
    }
```

**4. Subject:** avisa todos os inscritos.

📍 `observer/Subject.java` · [linhas 7–19](https://github.com/aland3r/driftor-reuso/blob/7c48276/backend/src/driftor/observer/Subject.java#L7-L19)

```java
public class Subject {
    private final List<Observer> observers = new ArrayList<>();

    public void inscrever(Observer observer) {
        observers.add(observer);
    }

    public void notificar(String evento, String mensagem) {
        for (Observer observer : observers) {
            observer.atualizar(evento, mensagem);
        }
    }
}
```

**5. Observador concreto:** a caixa do técnico guarda a mensagem, porque `manutencao_disparada` é um evento dele.

📍 `observer/AvisoNaTela.java` · [linhas 17–21](https://github.com/aland3r/driftor-reuso/blob/7c48276/backend/src/driftor/observer/AvisoNaTela.java#L17-L21)

```java
    public void atualizar(String evento, String mensagem) {
        if (eventos.contains(evento)) {
            mensagens.add(mensagem);
        }
    }
```

**6. Tela do técnico:** a cada troca de tela, o React pede os avisos do papel e mostra no topo.

📍 `frontend/src/main.jsx` · [linhas 21–21](https://github.com/aland3r/driftor-reuso/blob/7c48276/frontend/src/main.jsx#L21-L21)

```jsx
  useEffect(() => { if (papel()) api("GET", "/avisos").then(setAvisos); }, [local]);  // Observer: avisos do papel
```

📍 `acesso/AcessoController.java` · [linhas 18–21](https://github.com/aland3r/driftor-reuso/blob/7c48276/backend/src/driftor/acesso/AcessoController.java#L18-L21)

```java
    @GetMapping("/api/avisos")
    public List<String> avisos(@RequestHeader("Papel") String papel) {
        return Avisos.CAIXA_DO_PAPEL.get(papel).retirarMensagens();
    }
```

## Segundo exemplo

Subject `ANALISE`: quando uma análise termina, o gestor é avisado. [`AnaliseController.java:34`](https://github.com/aland3r/driftor-reuso/blob/7c48276/backend/src/driftor/analise/AnaliseController.java#L34) · inscrição em [`Avisos.java:21`](https://github.com/aland3r/driftor-reuso/blob/7c48276/backend/src/driftor/observer/Avisos.java#L21)
