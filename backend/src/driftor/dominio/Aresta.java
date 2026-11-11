package driftor.dominio;

/** Quantas vezes uma atividade veio logo depois da outra. */
public class Aresta {
    private final String origem;
    private final String destino;
    private final int frequencia;

    public Aresta(String origem, String destino, int frequencia) {
        this.origem = origem;
        this.destino = destino;
        this.frequencia = frequencia;
    }

    public String getOrigem() { return origem; }
    public String getDestino() { return destino; }
    public int getFrequencia() { return frequencia; }
}
