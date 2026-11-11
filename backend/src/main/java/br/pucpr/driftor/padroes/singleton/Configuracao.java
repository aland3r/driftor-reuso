package br.pucpr.driftor.padroes.singleton;

import java.util.Map;
import java.util.Set;
import org.springframework.http.HttpStatus;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.web.client.RestClient;
import org.springframework.web.server.ResponseStatusException;

/**
 * SINGLETON, exemplo 1: as configurações do app e as regras de cada papel, lidas uma vez só.
 * Toda chamada a Configuracao.getInstancia() devolve o MESMO objeto.
 */
public class Configuracao {
    private static Configuracao instancia;

    private final String urlDoBanco;
    private final RestClient motor;  // o motor Python (pm4py e ADWIN)

    /** VARIABILIDADE por papel: o que cada perfil pode fazer no mesmo produto. */
    private final Map<String, Papel> papeis = Map.of(
            "gestor", new Papel("Gestor", "/processos",
                    Set.of("processos", "atividades", "analises", "ver_analise", "manutencoes", "disparar_manutencao")),
            "tecnico", new Papel("Técnico de manutenção", "/manutencoes",
                    Set.of("manutencoes", "ver_analise", "concluir_manutencao")));

    public record Papel(String nome, String inicio, Set<String> pode) {}

    private Configuracao() {  // construtor privado: ninguém de fora faz new Configuracao()
        urlDoBanco = System.getenv().getOrDefault("DATABASE_URL", "postgresql://driftor_reuso:local@localhost:5432/driftor");
        motor = RestClient.builder().requestFactory(new SimpleClientHttpRequestFactory())
                .baseUrl(System.getenv().getOrDefault("MOTOR_URL", "http://localhost:8000")).build();
    }

    public static synchronized Configuracao getInstancia() {
        if (instancia == null) {
            instancia = new Configuracao();
        }
        return instancia;
    }

    /** VARIABILIDADE: se o papel não tem a permissão, a requisição para aqui com 403. */
    public void exigir(String papel, String permissao) {
        if (!papeis.containsKey(papel) || !papeis.get(papel).pode().contains(permissao)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Este perfil não tem acesso.");
        }
    }

    public Map<String, Papel> getPapeis() { return papeis; }
    public String getUrlDoBanco() { return urlDoBanco; }
    public RestClient getMotor() { return motor; }
}
