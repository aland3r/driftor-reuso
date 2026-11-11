package driftor.adapter;

import driftor.dominio.PontoDaSerie;
import java.util.List;

/** ADAPTER, exemplo 2 (Target): o que o app espera de quem detecta desvios numa série. */
public interface DetectorDeDrift {
    /** Devolve a posição onde cada desvio começa. */
    List<Integer> detectar(List<PontoDaSerie> serie, double delta);
}
