package driftor.atividade;

import driftor.compactacao.RepositorioBase;
import driftor.dominio.Atividade;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.UUID;

/** SQL do CRUD de Atividade. Listar, obter e excluir vêm de RepositorioBase. */
public class AtividadeRepositorio extends RepositorioBase<Atividade> {

    public AtividadeRepositorio() {
        super("atividades", "id, nome, descricao", "nome");
    }

    @Override
    protected Atividade criarObjeto(ResultSet linha) throws SQLException {
        return new Atividade(linha.getObject("id", UUID.class), linha.getString("nome"), linha.getString("descricao"));
    }

    // ---- Create
    public void inserir(Atividade atividade) {
        banco.executar("insert into atividades (id, nome, descricao) values (?, ?, ?)",
                atividade.getId(), atividade.getNome(), atividade.getDescricao());
    }

    // ---- Update
    public void atualizar(Atividade atividade) {
        banco.executar("update atividades set nome = ?, descricao = ? where id = ?",
                atividade.getNome(), atividade.getDescricao(), atividade.getId());
    }
}
