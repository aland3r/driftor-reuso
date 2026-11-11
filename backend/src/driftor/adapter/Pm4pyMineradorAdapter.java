package driftor.adapter;

import driftor.dominio.Aresta;
import driftor.dominio.Trace;
import driftor.singleton.Configuracao;
import java.util.List;
import java.util.Map;
import org.springframework.web.client.RestClient;

/**
 * ADAPTER, exemplo 1 (Adapter): o PM4Py roda no motor Python (o Adaptee) e fala outra língua:
 * recebe só as sequências de atividades e devolve {de, para, vezes}. Esta classe traduz nos dois sentidos.
 */
public class Pm4pyMineradorAdapter implements MineradorDeGrafo {
    private final RestClient motor = Configuracao.getInstancia().getMotor();

    record ArestaDoPm4py(String de, String para, int vezes) {}

    @Override
    public List<Aresta> descobrirArestas(List<Trace> traces) {
        List<List<String>> sequencias = traces.stream().map(Trace::sequencia).toList();
        ArestaDoPm4py[] resposta = motor.post().uri("/dfg").body(Map.of("traces", sequencias))
                .retrieve().body(ArestaDoPm4py[].class);
        return java.util.Arrays.stream(resposta).map(a -> new Aresta(a.de(), a.para(), a.vezes())).toList();
    }
}
