package br.pucpr.driftor.dominio;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/** Análise de desvios: a série de durações de um processo passada pelo ADWIN. */
public class Analise {
    private final UUID id;
    private final UUID processoId;
    private String nome;
    private final String atividade;
    private final double delta;
    private int totalObservacoes;
    private List<Drift> drifts = new ArrayList<>();

    public Analise(UUID id, UUID processoId, String nome, String atividade, double delta, int totalObservacoes) {
        this.id = id;
        this.processoId = processoId;
        this.nome = nome;
        this.atividade = atividade;
        this.delta = delta;
        this.totalObservacoes = totalObservacoes;
    }

    public static Analise criar(Processo processo, String atividade, double delta) {
        String nome = processo.getNome() + " · " + atividade;
        return new Analise(UUID.randomUUID(), processo.getId(), nome, atividade, delta, 0);
    }

    public void renomear(String novoNome) {
        this.nome = novoNome.trim();
    }

    /** Recebe onde cada desvio começa e calcula a média da série antes e depois dele. */
    public void registrarResultado(List<Double> valores, List<Integer> inicios) {
        totalObservacoes = valores.size();
        drifts = new ArrayList<>();
        for (int i = 0; i < inicios.size(); i++) {
            int comeco = i == 0 ? 0 : inicios.get(i - 1);
            int fim = i + 1 < inicios.size() ? inicios.get(i + 1) : valores.size();
            int inicio = inicios.get(i);
            drifts.add(new Drift(UUID.randomUUID(), i + 1, inicio,
                    media(valores.subList(comeco, inicio)), media(valores.subList(inicio, fim))));
        }
    }

    private static double media(List<Double> valores) {
        return valores.stream().mapToDouble(Double::doubleValue).average().orElse(0);
    }

    public void setDrifts(List<Drift> drifts) { this.drifts = drifts; }
    public UUID getId() { return id; }
    public UUID getProcessoId() { return processoId; }
    public String getNome() { return nome; }
    public String getAtividade() { return atividade; }
    public double getDelta() { return delta; }
    public int getTotalObservacoes() { return totalObservacoes; }
    public List<Drift> getDrifts() { return drifts; }
}
