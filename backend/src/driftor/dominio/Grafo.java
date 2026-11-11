package driftor.dominio;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class Grafo {
    private final List<No> nos;
    private final List<Aresta> arestas;

    public Grafo(List<No> nos, List<Aresta> arestas) {
        this.nos = nos;
        this.arestas = arestas;
    }

    /** Junta a frequência de cada atividade às arestas que o minerador descobriu. */
    public static Grafo montar(List<Trace> traces, List<Aresta> arestas) {
        Map<String, Long> frequencia = new LinkedHashMap<>();
        for (Trace trace : traces) {
            for (Evento evento : trace.getEventos()) {
                frequencia.merge(evento.getAtividade(), 1L, Long::sum);
            }
        }
        List<No> nos = new ArrayList<>();
        frequencia.forEach((atividade, n) -> nos.add(new No(atividade, n)));
        return new Grafo(nos, arestas);
    }

    /** Texto do diagrama que a tela desenha com o Mermaid. */
    public String paraMermaid() {
        Map<String, String> ids = new HashMap<>();
        StringBuilder texto = new StringBuilder("flowchart LR\n");
        for (No no : nos) {
            ids.put(no.getAtividade(), "n" + ids.size());
            texto.append("  ").append(ids.get(no.getAtividade())).append("[\"").append(no.rotulo()).append("\"]\n");
        }
        for (Aresta a : arestas) {
            texto.append("  ").append(ids.get(a.getOrigem())).append(" -->|").append(a.getFrequencia()).append("| ")
                 .append(ids.get(a.getDestino())).append("\n");
        }
        return texto.toString();
    }

    public List<No> getNos() { return nos; }
    public List<Aresta> getArestas() { return arestas; }
}
