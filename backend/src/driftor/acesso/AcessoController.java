package driftor.acesso;

import driftor.observer.Avisos;
import driftor.singleton.Configuracao;
import java.util.List;
import java.util.Map;
import org.springframework.web.bind.annotation.*;

/** Entrada simulada (sem senha): a tela pede os papéis e, depois de entrar, os avisos do papel. */
@RestController
public class AcessoController {

    @GetMapping("/api/papeis")
    public Map<String, Configuracao.Papel> papeis() {
        return Configuracao.getInstancia().getPapeis();
    }

    @GetMapping("/api/avisos")
    public List<String> avisos(@RequestHeader("Papel") String papel) {
        return Avisos.CAIXA_DO_PAPEL.get(papel).retirarMensagens();
    }
}
