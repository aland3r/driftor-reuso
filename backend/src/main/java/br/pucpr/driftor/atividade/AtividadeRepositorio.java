package br.pucpr.driftor.atividade;

import br.pucpr.driftor.padroes.singleton.BancoDeDados;
import br.pucpr.driftor.dominio.Atividade;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;
import java.util.UUID;

/** SQL do CRUD de Atividade. */
public class AtividadeRepositorio {

    private final BancoDeDados banco = BancoDeDados.getInstancia();

    // ---- Read
    public List<Atividade> listar() {
        return banco.consultar("select id, nome, descricao from atividades order by nome", (linha, n) -> criarObjeto(linha));
    }

    public Atividade obter(UUID id) {
        return banco.consultar("select id, nome, descricao from atividades where id = ?", (linha, n) -> criarObjeto(linha), id).get(0);
    }

    // ---- Delete
    public void excluir(UUID id) {
        banco.executar("delete from atividades where id = ?", id);
    }

    private Atividade criarObjeto(ResultSet linha) throws SQLException {
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
