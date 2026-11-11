package driftor.dominio;

import java.util.UUID;

public class Atividade {
    private final UUID id;
    private String nome;
    private String descricao;

    public Atividade(UUID id, String nome, String descricao) {
        this.id = id;
        this.nome = nome;
        this.descricao = descricao;
    }

    public static Atividade criar(String nome, String descricao) {
        return new Atividade(UUID.randomUUID(), nome.trim(), descricao.trim());
    }

    public void editar(String nome, String descricao) {
        this.nome = nome.trim();
        this.descricao = descricao.trim();
    }

    public UUID getId() { return id; }
    public String getNome() { return nome; }
    public String getDescricao() { return descricao; }
}
