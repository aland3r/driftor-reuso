package driftor.compactacao;

import driftor.singleton.BancoDeDados;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;
import java.util.UUID;

/**
 * COMPACTAÇÃO DE CÓDIGO: listar, obter e excluir eram iguais nos quatro repositórios e agora ficam aqui.
 * Cada repositório só diz a sua tabela, as suas colunas e como uma linha vira objeto.
 */
public abstract class RepositorioBase<T> {
    // SINGLETON em uso: todo repositório herda este campo e usa o mesmo BancoDeDados
    protected final BancoDeDados banco = BancoDeDados.getInstancia();
    private final String tabela;
    private final String colunas;
    private final String ordem;

    protected RepositorioBase(String tabela, String colunas, String ordem) {
        this.tabela = tabela;
        this.colunas = colunas;
        this.ordem = ordem;
    }

    protected abstract T criarObjeto(ResultSet linha) throws SQLException;

    // ---- Read
    public List<T> listar() {
        return banco.consultar("select " + colunas + " from " + tabela + " order by " + ordem, (linha, n) -> criarObjeto(linha));
    }

    public T obter(UUID id) {
        return banco.consultar("select " + colunas + " from " + tabela + " where id = ?", (linha, n) -> criarObjeto(linha), id).get(0);
    }

    // ---- Delete
    public void excluir(UUID id) {
        banco.executar("delete from " + tabela + " where id = ?", id);
    }
}
