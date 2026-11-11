package driftor.processo;

import driftor.analise.AnaliseRepositorio;
import driftor.dominio.Grafo;
import driftor.dominio.Processo;
import driftor.dominio.Trace;
import driftor.dominio.Variante;
import driftor.adapter.MineradorDeGrafo;
import driftor.adapter.Pm4pyMineradorAdapter;
import driftor.singleton.Configuracao;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

/** CRUD de Processo (só o gestor). */
@RestController
@RequestMapping("/api/processos")
public class ProcessoController {
    private final ProcessoRepositorio repositorio = new ProcessoRepositorio();
    private final MineradorDeGrafo minerador = new Pm4pyMineradorAdapter();

    // ---- Read: lista
    @GetMapping
    public List<Processo> listar(@RequestHeader("Papel") String papel) {
        Configuracao.getInstancia().exigir(papel, "processos");
        return repositorio.listar();
    }

    // ---- Create
    @PostMapping
    public Processo criar(@RequestHeader("Papel") String papel, @RequestBody Map<String, String> corpo) {
        Configuracao.getInstancia().exigir(papel, "processos");
        Processo processo = Processo.criar(corpo.get("nome"));
        repositorio.inserir(processo);
        return processo;
    }

    // ---- Read: detalhe com o grafo, as variantes e as análises
    @GetMapping("/{id}")
    public Map<String, Object> ver(@RequestHeader("Papel") String papel, @PathVariable UUID id) {
        Configuracao.getInstancia().exigir(papel, "processos");
        List<Trace> traces = repositorio.traces(id);
        Grafo grafo = Grafo.montar(traces, traces.isEmpty() ? List.of() : minerador.descobrirArestas(traces));
        return Map.of("processo", repositorio.obter(id), "mermaid", grafo.paraMermaid(), "atividades", grafo.getNos(),
                "variantes", Variante.agrupar(traces), "analises", new AnaliseRepositorio().doProcesso(id));
    }

    // ---- Update: carregar o log (as atividades aparecem direto no grafo)
    @PostMapping("/{id}/log")
    public void carregarLog(@RequestHeader("Papel") String papel, @PathVariable UUID id, @RequestParam MultipartFile arquivo) {
        Configuracao.getInstancia().exigir(papel, "processos");
        Processo processo = repositorio.obter(id);
        List<Trace> traces = LeitorDeLog.ler(arquivo);
        processo.carregarLog(arquivo.getOriginalFilename(), traces);
        repositorio.salvarLog(processo, traces);
    }

    // ---- Update: renomear
    @PutMapping("/{id}")
    public void renomear(@RequestHeader("Papel") String papel, @PathVariable UUID id, @RequestBody Map<String, String> corpo) {
        Configuracao.getInstancia().exigir(papel, "processos");
        Processo processo = repositorio.obter(id);
        processo.renomear(corpo.get("nome"));
        repositorio.atualizar(processo);
    }

    // ---- Delete
    @DeleteMapping("/{id}")
    public void excluir(@RequestHeader("Papel") String papel, @PathVariable UUID id) {
        Configuracao.getInstancia().exigir(papel, "processos");
        repositorio.excluir(id);
    }
}
