package br.pucpr.driftor.padroes.observer;

import java.util.Map;
import java.util.Set;

/**
 * OBSERVER no Driftor.
 * Exemplo 1: ANALISE avisa o gestor quando uma análise termina.
 * Exemplo 2: MANUTENCAO avisa o técnico (manutenção disparada) e o gestor (manutenção concluída).
 */
public class Avisos {
    public static final Subject ANALISE = new Subject();
    public static final Subject MANUTENCAO = new Subject();

    public static final Map<String, AvisoNaTela> CAIXA_DO_PAPEL = Map.of(
            "gestor", new AvisoNaTela(Set.of("analise_concluida", "manutencao_concluida")),
            "tecnico", new AvisoNaTela(Set.of("manutencao_disparada")));

    /** As inscrições: quem reage a cada evento é decidido aqui, não em quem publica. */
    public static void inscrever() {
        ANALISE.inscrever(CAIXA_DO_PAPEL.get("gestor"));
        MANUTENCAO.inscrever(CAIXA_DO_PAPEL.get("tecnico"));
        MANUTENCAO.inscrever(CAIXA_DO_PAPEL.get("gestor"));
    }
}
