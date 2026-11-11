package driftor.adapter;

import driftor.dominio.Aresta;
import driftor.dominio.Trace;
import java.util.List;

/** ADAPTER, exemplo 1 (Target): o que o app espera de quem descobre o grafo do processo. */
public interface MineradorDeGrafo {
    List<Aresta> descobrirArestas(List<Trace> traces);
}
