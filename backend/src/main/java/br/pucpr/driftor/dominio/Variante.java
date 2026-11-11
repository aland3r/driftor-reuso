package br.pucpr.driftor.dominio;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** Traces com a mesma sequência de atividades formam uma variante. */
public class Variante {
    private final int numero;
    private final List<String> sequencia;
    private final long totalTraces;

    public Variante(int numero, List<String> sequencia, long totalTraces) {
        this.numero = numero;
        this.sequencia = sequencia;
        this.totalTraces = totalTraces;
    }

    public static List<Variante> agrupar(List<Trace> traces) {
        Map<List<String>, Long> contagem = new LinkedHashMap<>();
        for (Trace trace : traces) {
            contagem.merge(trace.sequencia(), 1L, Long::sum);
        }
        List<Variante> variantes = new ArrayList<>();
        contagem.entrySet().stream()
                .sorted(Map.Entry.<List<String>, Long>comparingByValue().reversed())
                .forEach(e -> variantes.add(new Variante(variantes.size() + 1, e.getKey(), e.getValue())));
        return variantes;
    }

    public String getDescricao() {
        return String.join(" → ", sequencia);
    }

    public int getNumero() { return numero; }
    public long getTotalTraces() { return totalTraces; }
}
