package br.pucpr.driftor.padroes.singleton;

import com.zaxxer.hikari.HikariDataSource;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;
import org.springframework.core.io.ClassPathResource;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;

/**
 * SINGLETON, exemplo 2: UMA conexão (pool) com o Postgres para o app inteiro.
 * Todos os repositórios usam BancoDeDados.getInstancia() e recebem o mesmo objeto.
 */
public class BancoDeDados {
    private static BancoDeDados instancia;

    private final JdbcTemplate jdbc;

    private BancoDeDados() {
        URI url = URI.create(Configuracao.getInstancia().getUrlDoBanco());  // postgresql://usuario:senha@host:porta/banco
        String[] usuario = url.getUserInfo().split(":", 2);
        HikariDataSource conexoes = new HikariDataSource();
        conexoes.setJdbcUrl("jdbc:postgresql://" + url.getHost() + ":" + url.getPort() + url.getPath() + "?reWriteBatchedInserts=true");
        conexoes.setUsername(usuario[0]);
        conexoes.setPassword(usuario[1]);
        conexoes.setMaximumPoolSize(4);
        jdbc = new JdbcTemplate(conexoes);
    }

    public static synchronized BancoDeDados getInstancia() {
        if (instancia == null) {
            instancia = new BancoDeDados();
        }
        return instancia;
    }

    /** SELECT que vira objetos do domínio. */
    public <T> List<T> consultar(String sql, RowMapper<T> paraObjeto, Object... parametros) {
        return jdbc.query(sql, paraObjeto, parametros);
    }

    /** SELECT que vira linhas (coluna -> valor), para as listas com dados de várias tabelas. */
    public List<Map<String, Object>> consultarLinhas(String sql, Object... parametros) {
        return jdbc.queryForList(sql, parametros);
    }

    /** INSERT, UPDATE ou DELETE. */
    public void executar(String sql, Object... parametros) {
        jdbc.update(sql, parametros);
    }

    /** O mesmo INSERT para muitas linhas de uma vez. */
    public void executarVarios(String sql, List<Object[]> linhas) {
        jdbc.batchUpdate(sql, linhas);
    }

    public void criarTabelas() throws Exception {
        jdbc.execute(new ClassPathResource("schema.sql").getContentAsString(StandardCharsets.UTF_8));
    }
}
