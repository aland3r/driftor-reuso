package driftor.dominio;

import java.util.UUID;

public class Atividade {
    private final UUID id;
    private String nome;

    public Atividade(UUID id, String nome) {
        this.id = id;
        this.nome = nome;
    }

    public static Atividade criar(String nome) {
        return new Atividade(UUID.randomUUID(), nome.trim());
    }

    public void renomear(String novoNome) {
        this.nome = novoNome.trim();
    }

    public UUID getId() { return id; }
    public String getNome() { return nome; }
}
