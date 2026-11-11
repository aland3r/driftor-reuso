package br.pucpr.driftor.manutencao;

import br.pucpr.driftor.analise.AnaliseRepositorio;
import br.pucpr.driftor.dominio.Manutencao;
import br.pucpr.driftor.padroes.observer.Avisos;
import br.pucpr.driftor.padroes.singleton.Configuracao;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.springframework.web.bind.annotation.*;

/** CRUD de Manutenção. O gestor dispara e exclui; o técnico conclui. */
@RestController
public class ManutencaoController {
    private final ManutencaoRepositorio repositorio = new ManutencaoRepositorio();

    // ---- Read: lista (gestor e técnico)
    @GetMapping("/api/manutencoes")
    public List<Map<String, Object>> listar(@RequestHeader("Papel") String papel) {
        Configuracao.getInstancia().exigir(papel, "manutencoes");
        return repositorio.listarResumo(null);
    }

    // ---- Create: o gestor dispara a partir de um desvio
    @PostMapping("/api/analises/{analiseId}/manutencoes")
    public void disparar(@RequestHeader("Papel") String papel, @PathVariable UUID analiseId, @RequestBody Map<String, String> corpo) {
        Configuracao.getInstancia().exigir(papel, "disparar_manutencao");
        Manutencao manutencao = Manutencao.disparar(analiseId, UUID.fromString(corpo.get("driftId")), corpo.get("descricao"));
        repositorio.inserir(manutencao);
        Avisos.MANUTENCAO.notificar("manutencao_disparada", "Nova manutenção: " + manutencao.getDescricao());  // Observer
    }

    // ---- Read: detalhe
    @GetMapping("/api/manutencoes/{id}")
    public Map<String, Object> ver(@RequestHeader("Papel") String papel, @PathVariable UUID id) {
        Configuracao.getInstancia().exigir(papel, "manutencoes");
        Manutencao manutencao = repositorio.obter(id);
        return Map.of("manutencao", manutencao, "analise", new AnaliseRepositorio().obter(manutencao.getAnaliseId()));
    }

    // ---- Update: o técnico conclui com as observações
    @PutMapping("/api/manutencoes/{id}/concluir")
    public void concluir(@RequestHeader("Papel") String papel, @PathVariable UUID id, @RequestBody Map<String, String> corpo) {
        Configuracao.getInstancia().exigir(papel, "concluir_manutencao");
        Manutencao manutencao = repositorio.obter(id);
        manutencao.concluir(corpo.get("observacoes"));
        repositorio.atualizar(manutencao);
        Avisos.MANUTENCAO.notificar("manutencao_concluida", "Manutenção concluída: " + manutencao.getDescricao());  // Observer
    }

    // ---- Delete: só o gestor
    @DeleteMapping("/api/manutencoes/{id}")
    public void excluir(@RequestHeader("Papel") String papel, @PathVariable UUID id) {
        Configuracao.getInstancia().exigir(papel, "disparar_manutencao");
        repositorio.excluir(id);
    }
}
