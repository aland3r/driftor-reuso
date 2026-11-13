package driftor.atividade;

import driftor.compactacao.RepositorioBase;
import driftor.dominio.Atividade;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.UUID;

/** SQL do CRUD de Atividade. Listar, obter e excluir vêm de RepositorioBase. */
// COMPACTAÇÃO: "extends RepositorioBase" faz esta classe herdar listar, obter e excluir; aqui ficam só o SQL próprio (inserir, atualizar...)
public class AtividadeRepositorio extends RepositorioBase<Atividade> {

    public AtividadeRepositorio() {
        // informa a tabela, as colunas e a ordem que os métodos herdados usam
        super("atividades", "id, nome", "nome");
    }

    @Override
    protected Atividade criarObjeto(ResultSet linha) throws SQLException {
        return new Atividade(linha.getObject("id", UUID.class), linha.getString("nome"));
    }

    // ---- Create
    public void inserir(Atividade atividade) {
        banco.executar("insert into atividades (id, nome) values (?, ?)", atividade.getId(), atividade.getNome());
    }

    // ---- Update
    public void atualizar(Atividade atividade) {
        banco.executar("update atividades set nome = ? where id = ?", atividade.getNome(), atividade.getId());
    }
}
