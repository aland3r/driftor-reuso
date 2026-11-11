package br.pucpr.driftor;

import br.pucpr.driftor.padroes.observer.Avisos;
import br.pucpr.driftor.padroes.singleton.BancoDeDados;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class DriftorApplication {

    public static void main(String[] args) throws Exception {
        BancoDeDados.getInstancia().criarTabelas();
        Avisos.inscrever();
        SpringApplication.run(DriftorApplication.class, args);
    }
}
