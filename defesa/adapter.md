# Adapter

[← voltar](../README.md) · links fixos no commit `f10116b`

**O que é:** permite que objetos com **interfaces incompatíveis** trabalhem juntos. O Adapter fica no meio e traduz uma interface para a outra.

**Partes:**
- **Target:** a interface que o nosso código espera;
- **Adaptee:** quem faz o trabalho, mas fala outra "língua";
- **Adapter:** implementa o Target e, por dentro, chama o Adaptee, traduzindo os dados nos dois sentidos;
- **Client:** quem usa o Target sem saber quem está atrás.

**Por que usamos:** a detecção de desvios (ADWIN) e o grafo (PM4Py) rodam no motor Python, com outro formato de dados. O backend só conhece as nossas interfaces; trocar o motor exige mudar só o Adapter.

## Exemplo: detector de desvios

**Target:** o app quer passar a série e receber onde cada desvio começa.

📍 `adapter/DetectorDeDrift.java` · linhas 7–10 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/f10116b/backend/src/driftor/adapter/DetectorDeDrift.java#L7-L10)

```java
public interface DetectorDeDrift {
    /** Devolve a posição onde cada desvio começa. */
    List<Integer> detectar(List<PontoDaSerie> serie, double delta);
}
```

**Adapter:** transforma a série em uma lista de números, chama o ADWIN no motor e devolve só os inícios.

📍 `adapter/AdwinDetectorAdapter.java` · linhas 13–24 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/f10116b/backend/src/driftor/adapter/AdwinDetectorAdapter.java#L13-L24)

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

**Client:** o controller da Análise usa o Target: [`AnaliseController.java:32`](https://github.com/aland3r/driftor-reuso/blob/f10116b/backend/src/driftor/analise/AnaliseController.java#L32)

## Segundo exemplo

`MineradorDeGrafo` (Target) e `Pm4pyMineradorAdapter` (Adapter), usados para montar o grafo do processo: [`Pm4pyMineradorAdapter.java:14`](https://github.com/aland3r/driftor-reuso/blob/f10116b/backend/src/driftor/adapter/Pm4pyMineradorAdapter.java#L14) · uso em [`ProcessoController.java:45`](https://github.com/aland3r/driftor-reuso/blob/f10116b/backend/src/driftor/processo/ProcessoController.java#L45)
