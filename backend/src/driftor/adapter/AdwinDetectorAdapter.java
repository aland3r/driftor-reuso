package driftor.adapter;

import driftor.dominio.PontoDaSerie;
import driftor.singleton.Configuracao;
import java.util.List;
import java.util.Map;
import org.springframework.web.client.RestClient;

/**
 * ADAPTER, exemplo 2 (Adapter): o ADWIN da biblioteca river roda no motor Python (o Adaptee),
 * que quer só a lista de valores e responde {inicios: [...]}. Esta classe traduz nos dois sentidos.
 */
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
