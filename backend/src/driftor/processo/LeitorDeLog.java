package driftor.processo;

import driftor.dominio.Evento;
import driftor.dominio.Trace;
import driftor.singleton.Configuracao;
import java.time.OffsetDateTime;
import java.util.Arrays;
import java.util.List;
import org.springframework.http.MediaType;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.web.multipart.MultipartFile;

/** Manda o arquivo .xes para o motor Python, que devolve os traces já com início e duração de cada evento. */
public class LeitorDeLog {
    record EventoLido(String atividade, OffsetDateTime inicio, double duracao) {}
    record TraceLido(String caseId, List<EventoLido> eventos) {}

    public static List<Trace> ler(MultipartFile arquivo) {
        LinkedMultiValueMap<String, Object> corpo = new LinkedMultiValueMap<>();
        corpo.add("arquivo", arquivo.getResource());
        TraceLido[] lidos = Configuracao.getInstancia().getMotor().post().uri("/log").contentType(MediaType.MULTIPART_FORM_DATA).body(corpo)
                .retrieve().body(TraceLido[].class);
        return Arrays.stream(lidos).map(lido -> {
            Trace trace = new Trace(lido.caseId());
            lido.eventos().forEach(e -> trace.adicionar(new Evento(e.atividade(), e.inicio(), e.duracao())));
            return trace;
        }).toList();
    }
}
