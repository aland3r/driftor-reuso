package driftor.observer;

/** OBSERVER: quem quer ser avisado implementa esta interface. */
public interface Observer {
    void atualizar(String evento, String mensagem);
}
