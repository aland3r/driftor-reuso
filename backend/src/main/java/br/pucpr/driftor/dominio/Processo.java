package br.pucpr.driftor.dominio;

import java.util.List;
import java.util.UUID;

public class Processo {
    private final UUID id;
    private String nome;
    private String arquivo;
    private int totalTraces;
    private int totalEventos;

    public Processo(UUID id, String nome, String arquivo, int totalTraces, int totalEventos) {
        this.id = id;
        this.nome = nome;
        this.arquivo = arquivo;
        this.totalTraces = totalTraces;
        this.totalEventos = totalEventos;
    }

    public static Processo criar(String nome) {
        return new Processo(UUID.randomUUID(), nome.trim(), null, 0, 0);
    }

    public void renomear(String novoNome) {
        this.nome = novoNome.trim();
    }

    public void carregarLog(String arquivo, List<Trace> traces) {
        this.arquivo = arquivo;
        this.totalTraces = traces.size();
        this.totalEventos = traces.stream().mapToInt(t -> t.getEventos().size()).sum();
    }

    public UUID getId() { return id; }
    public String getNome() { return nome; }
    public String getArquivo() { return arquivo; }
    public int getTotalTraces() { return totalTraces; }
    public int getTotalEventos() { return totalEventos; }
}
