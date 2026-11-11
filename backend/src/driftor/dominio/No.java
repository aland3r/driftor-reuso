package driftor.dominio;

/** Uma atividade no grafo, com quantas vezes ela aparece no log. */
public class No {
    private final String atividade;
    private final long frequencia;

    public No(String atividade, long frequencia) {
        this.atividade = atividade;
        this.frequencia = frequencia;
    }

    public String rotulo() {
        return atividade + " (" + frequencia + ")";
    }

    public String getAtividade() { return atividade; }
    public long getFrequencia() { return frequencia; }
}
