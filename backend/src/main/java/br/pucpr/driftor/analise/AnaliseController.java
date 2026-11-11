package br.pucpr.driftor.analise;

import br.pucpr.driftor.dominio.Analise;
import br.pucpr.driftor.dominio.PontoDaSerie;
import br.pucpr.driftor.dominio.Processo;
import br.pucpr.driftor.manutencao.ManutencaoRepositorio;
import br.pucpr.driftor.padroes.adapter.AdwinDetectorAdapter;
import br.pucpr.driftor.padroes.adapter.DetectorDeDrift;
import br.pucpr.driftor.padroes.observer.Avisos;
import br.pucpr.driftor.padroes.singleton.Configuracao;
import br.pucpr.driftor.processo.ProcessoRepositorio;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.springframework.web.bind.annotation.*;

/** CRUD de Análise. O gestor faz tudo; o técnico só abre o detalhe. */
@RestController
public class AnaliseController {
    private final AnaliseRepositorio repositorio = new AnaliseRepositorio();
    private final DetectorDeDrift detector = new AdwinDetectorAdapter();

    // ---- Create: "Gerar análise de desvios" na página do processo
    @PostMapping("/api/processos/{processoId}/analises")
    public Analise criar(@RequestHeader("Papel") String papel, @PathVariable UUID processoId, @RequestBody Map<String, String> corpo) {
        Configuracao.getInstancia().exigir(papel, "analises");
        ProcessoRepositorio processos = new ProcessoRepositorio();
        Processo processo = processos.obter(processoId);
        Analise analise = Analise.criar(processo, corpo.get("atividade"), Double.parseDouble(corpo.get("delta")));
        List<PontoDaSerie> serie = PontoDaSerie.serieDeDuracao(processos.traces(processoId), analise.getAtividade());
        List<Double> valores = serie.stream().map(PontoDaSerie::getValor).toList();
        analise.registrarResultado(valores, detector.detectar(serie, analise.getDelta()));  // Adapter
        repositorio.inserir(analise, valores);
        Avisos.ANALISE.notificar("analise_concluida",  // Observer
                "Análise " + analise.getNome() + " concluída: " + analise.getDrifts().size() + " desvio(s).");
        return analise;
    }

    // ---- Read: detalhe com a série e os desvios (o técnico também vê)
    @GetMapping("/api/analises/{id}")
    public Map<String, Object> ver(@RequestHeader("Papel") String papel, @PathVariable UUID id) {
        Configuracao.getInstancia().exigir(papel, "ver_analise");
        Analise analise = repositorio.obter(id);
        return Map.of("analise", analise, "processo", new ProcessoRepositorio().obter(analise.getProcessoId()),
                "serie", repositorio.serie(id), "manutencoes", new ManutencaoRepositorio().listarResumo(id));
    }

    // ---- Update: renomear
    @PutMapping("/api/analises/{id}")
    public void renomear(@RequestHeader("Papel") String papel, @PathVariable UUID id, @RequestBody Map<String, String> corpo) {
        Configuracao.getInstancia().exigir(papel, "analises");
        Analise analise = repositorio.obter(id);
        analise.renomear(corpo.get("nome"));
        repositorio.renomear(analise);
    }

    // ---- Delete
    @DeleteMapping("/api/analises/{id}")
    public void excluir(@RequestHeader("Papel") String papel, @PathVariable UUID id) {
        Configuracao.getInstancia().exigir(papel, "analises");
        repositorio.excluir(id);
    }
}
