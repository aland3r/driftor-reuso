package br.pucpr.driftor.dominio;

import java.util.Comparator;
import java.util.List;
import java.util.stream.IntStream;

/** Uma observação da série que vai para o ADWIN: a duração de um trace. */
public class PontoDaSerie {
    private final int posicao;
    private final String caseId;
    private final double valor;

    public PontoDaSerie(int posicao, String caseId, double valor) {
        this.posicao = posicao;
        this.caseId = caseId;
        this.valor = valor;
    }

    /** Um ponto por trace, em ordem de início. */
    public static List<PontoDaSerie> serieDeDuracao(List<Trace> traces, String atividade) {
        List<Trace> ordenados = traces.stream().sorted(Comparator.comparing(Trace::inicio)).toList();
        return IntStream.range(0, ordenados.size())
                .mapToObj(i -> new PontoDaSerie(i, ordenados.get(i).getCaseId(), ordenados.get(i).duracao(atividade)))
                .toList();
    }

    public int getPosicao() { return posicao; }
    public String getCaseId() { return caseId; }
    public double getValor() { return valor; }
}
