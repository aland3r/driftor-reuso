# Adapter

[← defesa](../README.md) · links fixos no commit `dcd0d79`

**O que é:** permite que objetos com **interfaces incompatíveis** trabalhem juntos. O Adapter fica no meio e traduz de uma para a outra.

**Partes:** **Target** (a interface que o nosso código espera), **Adaptee** (quem faz o trabalho, mas fala outra "língua"), **Adapter** (implementa o Target e chama o Adaptee por dentro) e **Client** (quem usa o Target).

**Por que usamos:** o ADWIN e o PM4Py rodam no motor Python, com outro formato de dados. O backend só conhece as nossas interfaces; trocar o motor muda só o Adapter.

## Exemplo: detector de desvios, no caminho de "Gerar análise"

**1. Tela:** o botão **Gerar análise de desvios** chama a API.

📍 `frontend/src/telas/Processo.jsx` · [linhas 32–36](https://github.com/aland3r/driftor-reuso/blob/dcd0d79/frontend/src/telas/Processo.jsx#L32-L36)

```jsx
  const gerarAnalise = async (e) => {
    e.preventDefault();
    const analise = await api("POST", `/processos/${id}/analises`, { atividade, delta });
    navegar("/analises/" + analise.id);
  };
```

**2. Client (controller):** usa o detector pela interface, sem saber que é o ADWIN.

📍 `analise/AnaliseController.java` · [linhas 21–21](https://github.com/aland3r/driftor-reuso/blob/dcd0d79/backend/src/driftor/analise/AnaliseController.java#L21-L21)

```java
    private final DetectorDeDrift detector = new AdwinDetectorAdapter();
```

📍 `analise/AnaliseController.java` · [linhas 32–32](https://github.com/aland3r/driftor-reuso/blob/dcd0d79/backend/src/driftor/analise/AnaliseController.java#L32-L32)

```java
        analise.registrarResultado(valores, detector.detectar(serie, analise.getDelta()));  // Adapter
```

**3. Target:** o que o app espera: passar a série e receber onde cada desvio começa.

📍 `adapter/DetectorDeDrift.java` · [linhas 7–10](https://github.com/aland3r/driftor-reuso/blob/dcd0d79/backend/src/driftor/adapter/DetectorDeDrift.java#L7-L10)

```java
public interface DetectorDeDrift {
    /** Devolve a posição onde cada desvio começa. */
    List<Integer> detectar(List<PontoDaSerie> serie, double delta);
}
```

**4. Adapter:** transforma a série em uma lista de números, chama o ADWIN (Adaptee) no motor e devolve só os inícios.

📍 `adapter/AdwinDetectorAdapter.java` · [linhas 13–24](https://github.com/aland3r/driftor-reuso/blob/dcd0d79/backend/src/driftor/adapter/AdwinDetectorAdapter.java#L13-L24)

```java
public class AdwinDetectorAdapter implements DetectorDeDrift {
    private final RestClient motor = Configuracao.getInstancia().getMotor();

    record RespostaDoAdwin(List<Integer> inicios) {}

    @Override
    public List<Integer> detectar(List<PontoDaSerie> serie, double delta) {
        List<Double> valores = serie.stream().map(PontoDaSerie::getValor).toList();
        return motor.post().uri("/adwin").body(Map.of("valores", valores, "delta", delta))
                .retrieve().body(RespostaDoAdwin.class).inicios();
    }
}
```

## Segundo exemplo

`MineradorDeGrafo` (Target) e `Pm4pyMineradorAdapter` (Adapter), usados ao abrir o processo para montar o grafo: [`Pm4pyMineradorAdapter.java:14`](https://github.com/aland3r/driftor-reuso/blob/dcd0d79/backend/src/driftor/adapter/Pm4pyMineradorAdapter.java#L14) · uso em [`ProcessoController.java:45`](https://github.com/aland3r/driftor-reuso/blob/dcd0d79/backend/src/driftor/processo/ProcessoController.java#L45)
