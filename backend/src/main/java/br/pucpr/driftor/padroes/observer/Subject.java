package br.pucpr.driftor.padroes.observer;

import java.util.ArrayList;
import java.util.List;

/** OBSERVER: guarda os inscritos e avisa todos. Não sabe quem eles são nem o que fazem. */
public class Subject {
    private final List<Observer> observers = new ArrayList<>();

    public void inscrever(Observer observer) {
        observers.add(observer);
    }

    public void notificar(String evento, String mensagem) {
        for (Observer observer : observers) {
            observer.atualizar(evento, mensagem);
        }
    }
}
