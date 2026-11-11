package driftor.manutencao;

import driftor.compactacao.RepositorioBase;
import driftor.dominio.Manutencao;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/** SQL do CRUD de Manutenção. Listar, obter e excluir vêm de RepositorioBase. */
public class ManutencaoRepositorio extends RepositorioBase<Manutencao> {

    public ManutencaoRepositorio() {
        super("manutencoes", "id, analise_id, drift_id, descricao, status, observacoes", "status desc");
    }

    @Override
    protected Manutencao criarObjeto(ResultSet linha) throws SQLException {
        return new Manutencao(linha.getObject("id", UUID.class), linha.getObject("analise_id", UUID.class),
                linha.getObject("drift_id", UUID.class), linha.getString("descricao"), linha.getString("status"),
                linha.getString("observacoes"));
    }

    // ---- Read: a lista com o nome da análise, do processo e o número do desvio
    public List<Map<String, Object>> listarResumo(UUID analiseId) {
        return banco.consultarLinhas("""
                select m.id, m.descricao, m.status, a.id as analise_id, a.nome as analise, p.nome as processo, d.posicao as desvio
                from manutencoes m join analises a on a.id = m.analise_id join processos p on p.id = a.processo_id
                join drifts d on d.id = m.drift_id
                where ?::uuid is null or m.analise_id = ? order by m.status desc""", analiseId, analiseId);
    }

    // ---- Create
    public void inserir(Manutencao manutencao) {
        banco.executar("insert into manutencoes (id, analise_id, drift_id, descricao) values (?, ?, ?, ?)",
                manutencao.getId(), manutencao.getAnaliseId(), manutencao.getDriftId(), manutencao.getDescricao());
    }

    // ---- Update
    public void atualizar(Manutencao manutencao) {
        banco.executar("update manutencoes set status = ?, observacoes = ? where id = ?",
                manutencao.getStatus(), manutencao.getObservacoes(), manutencao.getId());
    }
}
