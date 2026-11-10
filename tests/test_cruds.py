"""Create, Read, Update e Delete de Atividade e de Nota de drift, e a variabilidade por edição."""

import re

from driftor.config import Configuracao


def test_crud_de_atividade(cliente):
    cliente.post("/atividades", data={"nome": "  Troca   de ferramenta ", "descricao": "setup"})
    tela = cliente.get("/atividades").text
    assert "Troca de ferramenta" in tela
    id = re.search(r"/atividades/([0-9a-f-]{36})/editar", tela).group(1)

    cliente.post(f"/atividades/{id}", data={"nome": "Setup", "descricao": "troca"})
    assert "Setup" in cliente.get("/atividades").text

    duplicada = cliente.post("/atividades", data={"nome": "setup"})
    assert duplicada.status_code == 422

    cliente.post(f"/atividades/{id}/excluir")
    assert "O catálogo está vazio" in cliente.get("/atividades").text


def test_crud_de_nota(cliente):
    banco = __import__("driftor.banco", fromlist=["BancoDeDados"]).BancoDeDados()
    banco.executar("insert into processos (id, nome, status) values ('00000000-0000-0000-0000-000000000001', 'P', 'pronto')")
    banco.executar("""insert into analises (id, processo_id, nome, delta, tratamento, total_observacoes, total_drifts, serie)
                      values ('00000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', 'A', 0.002, 'bruto', 3, 1, '[1,2,3]')""")
    banco.executar("""insert into drifts (id, analise_id, posicao, indice, inicio_anomalia, media_antes, media_depois, variacao_pct)
                      values ('00000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000002', 1, 2, 1, 1, 2.5, 150)""")
    analise = "/analises/00000000-0000-0000-0000-000000000002"

    tela = cliente.post("/notas", data={"drift_id": "00000000-0000-0000-0000-000000000003", "texto": "Troca de rolamento"}).text
    assert "Troca de rolamento" in tela and "Nota salva." in tela  # aviso do Observer
    assert banco.consultar_um("select total_notas from analises")["total_notas"] == 1  # ContadorDeNotas

    nota = re.search(r"/notas/([0-9a-f-]{36})/editar", tela).group(1)
    cliente.post(f"/notas/{nota}", data={"texto": "Rolamento trocado"})
    assert "Rolamento trocado" in cliente.get(f"{analise}/notas").text

    cliente.post(f"/notas/{nota}/excluir")
    assert "Nenhuma nota ainda" in cliente.get(f"{analise}/notas").text
    assert banco.consultar_um("select total_notas from analises")["total_notas"] == 0


def test_edicao_essencial_esconde_analises(cliente):
    config = Configuracao()
    config.edicao = "essencial"
    try:
        assert cliente.get("/analises").status_code == 404
        assert 'href="/analises"' not in cliente.get("/processos").text
    finally:
        config.edicao = "completa"
    assert cliente.get("/analises").status_code == 200


def test_singletons_devolvem_o_mesmo_objeto():
    from driftor.banco import BancoDeDados

    assert Configuracao() is Configuracao()
    assert BancoDeDados() is BancoDeDados()
