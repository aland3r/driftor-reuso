package br.pucpr.driftor.analise;

import br.pucpr.driftor.compactacao.RepositorioBase;
import br.pucpr.driftor.dominio.Analise;
import br.pucpr.driftor.dominio.Drift;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Arrays;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

/** SQL do CRUD de Análise (tabelas analises e drifts). Listar, obter e excluir vêm de RepositorioBase. */
public class AnaliseRepositorio extends RepositorioBase<Analise> {

    public AnaliseRepositorio() {
        super("analises", "id, processo_id, nome, atividade, delta, total_observacoes", "nome");
    }

    /** A análise vem com os seus desvios. */
    @Override
    protected Analise criarObjeto(ResultSet linha) throws SQLException {
        Analise analise = new Analise(linha.getObject("id", UUID.class), linha.getObject("processo_id", UUID.class),
                linha.getString("nome"), linha.getString("atividade"), linha.getDouble("delta"), linha.getInt("total_observacoes"));
        analise.setDrifts(banco.consultar(
                "select id, posicao, inicio, media_antes, media_depois from drifts where analise_id = ? order by posicao",
                (d, n) -> new Drift(d.getObject("id", UUID.class), d.getInt("posicao"), d.getInt("inicio"),
                        d.getDouble("media_antes"), d.getDouble("media_depois")),
                analise.getId()));
        return analise;
    }

    // ---- Read
    public List<Analise> doProcesso(UUID processoId) {
        return banco.consultar("select id, processo_id, nome, atividade, delta, total_observacoes from analises where processo_id = ?",
                (linha, n) -> criarObjeto(linha), processoId);
    }

    public List<Double> serie(UUID id) {
        String serie = banco.consultarLinhas("select serie from analises where id = ?", id).get(0).get("serie").toString();
        return Arrays.stream(serie.split(",")).map(Double::valueOf).toList();
    }

    // ---- Create
    public void inserir(Analise analise, List<Double> serie) {
        banco.executar("insert into analises (id, processo_id, nome, atividade, delta, total_observacoes, serie) values (?, ?, ?, ?, ?, ?, ?)",
                analise.getId(), analise.getProcessoId(), analise.getNome(), analise.getAtividade(), analise.getDelta(),
                analise.getTotalObservacoes(), serie.stream().map(String::valueOf).collect(Collectors.joining(",")));
        banco.executarVarios("insert into drifts (id, analise_id, posicao, inicio, media_antes, media_depois) values (?, ?, ?, ?, ?, ?)",
                analise.getDrifts().stream().map(d -> new Object[] {d.getId(), analise.getId(), d.getPosicao(), d.getInicio(),
                        d.getMediaAntes(), d.getMediaDepois()}).toList());
    }

    // ---- Update
    public void renomear(Analise analise) {
        banco.executar("update analises set nome = ? where id = ?", analise.getNome(), analise.getId());
    }
}
