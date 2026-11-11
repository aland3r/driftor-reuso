package driftor.analise;

import driftor.dominio.Analise;
import driftor.dominio.PontoDaSerie;
import driftor.dominio.Processo;
import driftor.manutencao.ManutencaoRepositorio;
import driftor.adapter.AdwinDetectorAdapter;
import driftor.adapter.DetectorDeDrift;
import driftor.observer.Avisos;
import driftor.singleton.Configuracao;
import driftor.processo.ProcessoRepositorio;
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
