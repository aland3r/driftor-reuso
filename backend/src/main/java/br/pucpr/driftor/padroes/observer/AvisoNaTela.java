package br.pucpr.driftor.padroes.observer;

import java.util.ArrayList;
import java.util.List;
import java.util.Set;

/** OBSERVER: a caixa de avisos de um papel. Guarda só os eventos que interessam a ele até a próxima tela. */
public class AvisoNaTela implements Observer {
    private final Set<String> eventos;
    private final List<String> mensagens = new ArrayList<>();

    public AvisoNaTela(Set<String> eventos) {
        this.eventos = eventos;
    }

    @Override
    public void atualizar(String evento, String mensagem) {
        if (eventos.contains(evento)) {
            mensagens.add(mensagem);
        }
    }

    public List<String> retirarMensagens() {
        List<String> lidas = List.copyOf(mensagens);
        mensagens.clear();
        return lidas;
    }
}
