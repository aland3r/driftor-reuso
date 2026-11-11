package br.pucpr.driftor.padroes.observer;

/** OBSERVER: quem quer ser avisado implementa esta interface. */
public interface Observer {
    void atualizar(String evento, String mensagem);
}
