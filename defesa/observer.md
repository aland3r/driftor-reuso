# Observer

[← voltar](../README.md) · links fixos no commit `82162ab`

**O que é:** um mecanismo de **assinatura**. Vários objetos se inscrevem para ser avisados quando algo acontece em outro objeto.

**Partes:**
- **Subject:** guarda a lista de inscritos e tem `inscrever` e `notificar`;
- **Observer:** a interface que todo inscrito implementa (`atualizar`);
- **observador concreto:** o que cada inscrito faz quando é avisado.

**Por que usamos:** quem publica o evento (o controller) não precisa saber quem quer ser avisado. Para acrescentar uma reação, basta inscrever outro observador.

📍 `padroes/observer/Subject.java` · linhas 7–19 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/padroes/observer/Subject.java#L7-L19)

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

📍 `padroes/observer/Observer.java` · linhas 4–6 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/padroes/observer/Observer.java#L4-L6)

```java
public interface Observer {
    void atualizar(String evento, String mensagem);
}
```

## Exemplo: análise concluída avisa o gestor

1. **Observador concreto:** `AvisoNaTela`, a caixa de avisos de um papel. Ela só guarda os eventos que interessam a esse papel. [`AvisoNaTela.java:17`](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/padroes/observer/AvisoNaTela.java#L17)
2. **Inscrição:** a caixa do gestor se inscreve no Subject `ANALISE`. [`Avisos.java:21`](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/padroes/observer/Avisos.java#L21)
3. **Publicação:** ao terminar a análise, o controller notifica. [`AnaliseController.java:34`](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/analise/AnaliseController.java#L34)
4. Na próxima tela, o React pede os avisos do papel e mostra o aviso no topo. [`AcessoController.java:20`](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/acesso/AcessoController.java#L20)

📍 `padroes/observer/Avisos.java` · linhas 12–24 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/padroes/observer/Avisos.java#L12-L24)

```java
    public static final Subject ANALISE = new Subject();
    public static final Subject MANUTENCAO = new Subject();

    public static final Map<String, AvisoNaTela> CAIXA_DO_PAPEL = Map.of(
            "gestor", new AvisoNaTela(Set.of("analise_concluida", "manutencao_concluida")),
            "tecnico", new AvisoNaTela(Set.of("manutencao_disparada")));

    /** As inscrições: quem reage a cada evento é decidido aqui, não em quem publica. */
    public static void inscrever() {
        ANALISE.inscrever(CAIXA_DO_PAPEL.get("gestor"));
        MANUTENCAO.inscrever(CAIXA_DO_PAPEL.get("tecnico"));
        MANUTENCAO.inscrever(CAIXA_DO_PAPEL.get("gestor"));
    }
```

## Segundo exemplo

Subject `MANUTENCAO`: quando o gestor dispara uma manutenção, o técnico é avisado; quando o técnico conclui, o gestor é avisado. [`ManutencaoController.java:30`](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/manutencao/ManutencaoController.java#L30) · [`ManutencaoController.java:48`](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/manutencao/ManutencaoController.java#L48)
