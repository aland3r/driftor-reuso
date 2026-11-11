package br.pucpr.driftor.dominio;

import java.util.UUID;

/** Um desvio: o ponto da série onde a duração mudou de nível. */
public class Drift {
    private final UUID id;
    private final int posicao;
    private final int inicio;
    private final double mediaAntes;
    private final double mediaDepois;

    public Drift(UUID id, int posicao, int inicio, double mediaAntes, double mediaDepois) {
        this.id = id;
        this.posicao = posicao;
        this.inicio = inicio;
        this.mediaAntes = mediaAntes;
        this.mediaDepois = mediaDepois;
    }

    public double variacaoPct() {
        return (mediaDepois - mediaAntes) / mediaAntes * 100;
    }

    public String getResumo() {
        String sentido = mediaDepois > mediaAntes ? "subiu" : "caiu";
        return String.format("A duração %s %.1f%% a partir do trace %d.", sentido, Math.abs(variacaoPct()), inicio);
    }

    public UUID getId() { return id; }
    public int getPosicao() { return posicao; }
    public int getInicio() { return inicio; }
    public double getMediaAntes() { return mediaAntes; }
    public double getMediaDepois() { return mediaDepois; }
}
