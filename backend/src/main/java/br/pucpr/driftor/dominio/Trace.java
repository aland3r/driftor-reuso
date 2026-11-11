package br.pucpr.driftor.dominio;

import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.List;

/** Uma execução do processo (um "case" do log), com os seus eventos em ordem. */
public class Trace {
    private final String caseId;
    private final List<Evento> eventos = new ArrayList<>();

    public Trace(String caseId) {
        this.caseId = caseId;
    }

    public void adicionar(Evento evento) {
        eventos.add(evento);
    }

    public OffsetDateTime inicio() {
        return eventos.get(0).getInicio();
    }

    public List<String> sequencia() {
        return eventos.stream().map(Evento::getAtividade).toList();
    }

    /** Soma das durações do trace inteiro (atividade = null) ou de uma atividade só. */
    public double duracao(String atividade) {
        return eventos.stream().filter(e -> e.eDaAtividade(atividade)).mapToDouble(Evento::getDuracao).sum();
    }

    public String getCaseId() { return caseId; }
    public List<Evento> getEventos() { return eventos; }
}
