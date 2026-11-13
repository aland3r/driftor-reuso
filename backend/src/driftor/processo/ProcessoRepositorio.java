package driftor.processo;

import driftor.compactacao.RepositorioBase;
import driftor.dominio.Evento;
import driftor.dominio.Processo;
import driftor.dominio.Trace;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/** SQL do CRUD de Processo (tabelas processos e eventos). Listar, obter e excluir vêm de RepositorioBase. */
// COMPACTAÇÃO: "extends RepositorioBase" faz esta classe herdar listar, obter e excluir; aqui ficam só o SQL próprio (inserir, atualizar...)
public class ProcessoRepositorio extends RepositorioBase<Processo> {

    public ProcessoRepositorio() {
        // informa a tabela, as colunas e a ordem que os métodos herdados usam
        super("processos", "id, nome, arquivo, total_traces, total_eventos", "nome");
    }

    @Override
    protected Processo criarObjeto(ResultSet linha) throws SQLException {
        return new Processo(linha.getObject("id", UUID.class), linha.getString("nome"), linha.getString("arquivo"),
                linha.getInt("total_traces"), linha.getInt("total_eventos"));
    }

    // ---- Create
    public void inserir(Processo processo) {
        banco.executar("insert into processos (id, nome) values (?, ?)", processo.getId(), processo.getNome());
    }

    // ---- Update
    public void atualizar(Processo processo) {
        banco.executar("update processos set nome = ?, arquivo = ?, total_traces = ?, total_eventos = ? where id = ?",
                processo.getNome(), processo.getArquivo(), processo.getTotalTraces(), processo.getTotalEventos(), processo.getId());
    }

    /** Grava as atividades novas do log e os eventos ligados a elas. */
    public void salvarLog(Processo processo, List<Trace> traces) {
        List<Object[]> eventos = new ArrayList<>();
        for (Trace trace : traces) {
            for (int ordem = 0; ordem < trace.getEventos().size(); ordem++) {
                Evento e = trace.getEventos().get(ordem);
                eventos.add(new Object[] {processo.getId(), trace.getCaseId(), ordem, e.getInicio(), e.getDuracao(), e.getAtividade()});
            }
        }
        List<Object[]> atividades = eventos.stream().map(e -> e[5]).distinct()
                .map(nome -> new Object[] {UUID.randomUUID(), nome}).toList();
        banco.executarVarios("insert into atividades (id, nome) values (?, ?) on conflict (nome) do nothing", atividades);
        banco.executar("delete from eventos where processo_id = ?", processo.getId());
        banco.executarVarios("""
                insert into eventos (processo_id, case_id, ordem, inicio, duracao, atividade_id)
                select ?, ?, ?, ?, ?, id from atividades where nome = ?""", eventos);
        atualizar(processo);
    }

    // ---- Read: os traces voltam montados a partir dos eventos
    public List<Trace> traces(UUID processoId) {
        Map<String, Trace> traces = new LinkedHashMap<>();
        banco.consultar("""
                select e.case_id, a.nome, e.inicio, e.duracao from eventos e join atividades a on a.id = e.atividade_id
                where e.processo_id = ? order by e.case_id, e.ordem""", (linha, n) -> {
            traces.computeIfAbsent(linha.getString("case_id"), Trace::new).adicionar(new Evento(
                    linha.getString("nome"), linha.getObject("inicio", java.time.OffsetDateTime.class), linha.getDouble("duracao")));
            return null;
        }, processoId);
        return new ArrayList<>(traces.values());
    }
}
