"""CRUDs de Atividade e de Manutenção, e a variabilidade por papel (Gestor e Técnico)."""

import re

from driftor.banco import BancoDeDados
from driftor.config import Configuracao

ANALISE = "00000000-0000-0000-0000-000000000002"
DRIFT = "00000000-0000-0000-0000-000000000003"


def entrar(cliente, papel):
    cliente.post("/entrar", data={"papel": papel}, follow_redirects=False)


def _analise_com_um_desvio():
    banco = BancoDeDados()
    banco.executar("insert into processos (id, nome, status) values ('00000000-0000-0000-0000-000000000001', 'Torno 02', 'pronto')")
    banco.executar(f"""insert into analises (id, processo_id, nome, delta, tratamento, total_observacoes, total_drifts, serie)
                      values ('{ANALISE}', '00000000-0000-0000-0000-000000000001', 'Análise A', 0.002, 'bruto', 3, 1, '[1,2,3]')""")
    banco.executar(f"""insert into drifts (id, analise_id, posicao, indice, inicio_anomalia, media_antes, media_depois, variacao_pct)
                      values ('{DRIFT}', '{ANALISE}', 1, 2, 1, 1, 2.5, 150)""")


def test_sem_perfil_vai_para_a_entrada(cliente):
    resposta = cliente.get("/processos", follow_redirects=False)
    assert resposta.headers["location"] == "/entrar"


def test_crud_de_atividade(cliente):
    entrar(cliente, "gestor")
    cliente.post("/atividades", data={"nome": "  Troca   de ferramenta ", "descricao": "setup"})
    tela = cliente.get("/atividades").text
    assert "Troca de ferramenta" in tela
    id = re.search(r"/atividades/([0-9a-f-]{36})/editar", tela).group(1)

    cliente.post(f"/atividades/{id}", data={"nome": "Setup", "descricao": "troca"})
    assert "Setup" in cliente.get("/atividades").text
    assert cliente.post("/atividades", data={"nome": "setup"}).status_code == 422  # nome repetido

    cliente.post(f"/atividades/{id}/excluir")
    assert "O catálogo está vazio" in cliente.get("/atividades").text


def test_fluxo_da_manutencao_entre_gestor_e_tecnico(cliente):
    _analise_com_um_desvio()

    # Gestor dispara (Create)
    entrar(cliente, "gestor")
    cliente.post(f"/analises/{ANALISE}/manutencoes", data={"drift_id": DRIFT, "descricao": "Verificar rolamento"})
    assert "Verificar rolamento" in cliente.get(f"/analises/{ANALISE}").text

    # Técnico recebe o aviso (Observer) e vê a lista (Read)
    entrar(cliente, "tecnico")
    tela = cliente.get("/manutencoes").text
    assert "Nova manutenção: Verificar rolamento" in tela
    id = re.search(r"/manutencoes/([0-9a-f-]{36})", tela).group(1)

    # Técnico conclui com observações (Update)
    cliente.post(f"/manutencoes/{id}/concluir", data={"observacoes": "Rolamento trocado"})
    tela = cliente.get(f"/manutencoes/{id}").text
    assert "Rolamento trocado" in tela and "concluída" in tela

    # Gestor recebe o aviso da conclusão (Observer) e exclui (Delete)
    entrar(cliente, "gestor")
    assert "Manutenção concluída pelo técnico" in cliente.get("/manutencoes").text
    cliente.post(f"/manutencoes/{id}/excluir")
    assert "Nenhuma manutenção disparada ainda" in cliente.get("/manutencoes").text


def test_variabilidade_por_papel(cliente):
    _analise_com_um_desvio()
    entrar(cliente, "tecnico")
    menu = cliente.get("/manutencoes").text
    assert 'href="/processos"' not in menu and 'href="/manutencoes"' in menu
    assert cliente.get("/processos").status_code == 403
    assert cliente.get("/analises").status_code == 403
    assert cliente.post(f"/analises/{ANALISE}/manutencoes", data={"drift_id": DRIFT, "descricao": "x"}).status_code == 403
    analise = cliente.get(f"/analises/{ANALISE}")  # o técnico vê a análise de origem, sem editar
    assert analise.status_code == 200 and "Renomear" not in analise.text and "Disparar manutenção" not in analise.text

    entrar(cliente, "gestor")
    assert cliente.get("/processos").status_code == 200
    assert "Disparar manutenção" in cliente.get(f"/analises/{ANALISE}").text


def test_singletons_devolvem_o_mesmo_objeto():
    assert Configuracao() is Configuracao()
    assert BancoDeDados() is BancoDeDados()
