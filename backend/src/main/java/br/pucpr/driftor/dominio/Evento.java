package br.pucpr.driftor.dominio;

import java.time.OffsetDateTime;

public class Evento {
    private final String atividade;
    private final OffsetDateTime inicio;
    private final double duracao;  // segundos

    public Evento(String atividade, OffsetDateTime inicio, double duracao) {
        this.atividade = atividade;
        this.inicio = inicio;
        this.duracao = duracao;
    }

    public boolean eDaAtividade(String nome) {
        return nome == null || nome.equals(atividade);
    }

    public String getAtividade() { return atividade; }
    public OffsetDateTime getInicio() { return inicio; }
    public double getDuracao() { return duracao; }
}
