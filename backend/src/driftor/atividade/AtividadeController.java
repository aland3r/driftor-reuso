package driftor.atividade;

import driftor.dominio.Atividade;
import driftor.singleton.Configuracao;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.springframework.web.bind.annotation.*;

/** CRUD de Atividade (só o gestor). O upload do log também cria atividades. */
@RestController
@RequestMapping("/api/atividades")
public class AtividadeController {
    private final AtividadeRepositorio repositorio = new AtividadeRepositorio();

    // ---- Read
    @GetMapping
    public List<Atividade> listar(@RequestHeader("Papel") String papel) {
        Configuracao.getInstancia().exigir(papel, "atividades");
        return repositorio.listar();
    }

    // ---- Create
    @PostMapping
    public void criar(@RequestHeader("Papel") String papel, @RequestBody Map<String, String> corpo) {
        Configuracao.getInstancia().exigir(papel, "atividades");
        repositorio.inserir(Atividade.criar(corpo.get("nome"), corpo.get("descricao")));
    }

    // ---- Update
    @PutMapping("/{id}")
    public void editar(@RequestHeader("Papel") String papel, @PathVariable UUID id, @RequestBody Map<String, String> corpo) {
        Configuracao.getInstancia().exigir(papel, "atividades");
        Atividade atividade = repositorio.obter(id);
        atividade.editar(corpo.get("nome"), corpo.get("descricao"));
        repositorio.atualizar(atividade);
    }

    // ---- Delete
    @DeleteMapping("/{id}")
    public void excluir(@RequestHeader("Papel") String papel, @PathVariable UUID id) {
        Configuracao.getInstancia().exigir(papel, "atividades");
        repositorio.excluir(id);
    }
}
