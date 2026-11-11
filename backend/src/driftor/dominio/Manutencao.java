package driftor.dominio;

import java.util.UUID;

/** Ordem de manutenção: o gestor dispara a partir de um desvio e o técnico conclui. */
public class Manutencao {
    private final UUID id;
    private final UUID analiseId;
    private final UUID driftId;
    private final String descricao;
    private String status;
    private String observacoes;

    public Manutencao(UUID id, UUID analiseId, UUID driftId, String descricao, String status, String observacoes) {
        this.id = id;
        this.analiseId = analiseId;
        this.driftId = driftId;
        this.descricao = descricao;
        this.status = status;
        this.observacoes = observacoes;
    }

    public static Manutencao disparar(UUID analiseId, UUID driftId, String descricao) {
        return new Manutencao(UUID.randomUUID(), analiseId, driftId, descricao.trim(), "pendente", "");
    }

    public boolean estaPendente() {
        return status.equals("pendente");
    }

    public void concluir(String observacoes) {
        this.status = "concluída";
        this.observacoes = observacoes.trim();
    }

    public UUID getId() { return id; }
    public UUID getAnaliseId() { return analiseId; }
    public UUID getDriftId() { return driftId; }
    public String getDescricao() { return descricao; }
    public String getStatus() { return status; }
    public String getObservacoes() { return observacoes; }
}
