import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import mermaid from "mermaid";
import { api } from "../api";
import { BotaoExcluir, FormRenomear, Tabela } from "../componentes";

mermaid.initialize({ startOnLoad: false, theme: "base", flowchart: { htmlLabels: false },
  themeVariables: { primaryColor: "#2b3849", primaryTextColor: "#e2e8f0", primaryBorderColor: "#4d8fc0", lineColor: "#91a0b5" } });

export default function Processo() {
  const { id } = useParams();
  const [dados, setDados] = useState(null);
  const [atividade, setAtividade] = useState("Machine_Operating");
  const [delta, setDelta] = useState("0.002");
  const grafo = useRef();
  const navegar = useNavigate();
  const carregar = () => api("GET", "/processos/" + id).then(setDados);
  useEffect(() => { carregar(); }, [id]);
  useEffect(() => {
    if (dados?.atividades.length) mermaid.render("grafo", dados.mermaid).then(({ svg }) => { grafo.current.innerHTML = svg; });
  }, [dados]);
  if (!dados) return null;
  const { processo, atividades, variantes, analises } = dados;

  const carregarLog = async (e) => {
    e.preventDefault();
    await api("POST", `/processos/${id}/log`, new FormData(e.target));
    carregar();
  };
  const renomear = async (nome) => { await api("PUT", "/processos/" + id, { nome }); carregar(); };
  const excluir = async () => { await api("DELETE", "/processos/" + id); navegar("/processos"); };
  const gerarAnalise = async (e) => {
    e.preventDefault();
    const analise = await api("POST", `/processos/${id}/analises`, { atividade, delta });
    navegar("/analises/" + analise.id);
  };

  return (
    <>
      <div className="page-head">
        <div><h1>{processo.nome}</h1><div className="meta">{processo.arquivo} · {processo.totalTraces} traces · {processo.totalEventos} eventos</div></div>
        <BotaoExcluir aoExcluir={excluir} rotulo="Excluir processo" />
      </div>
      <section className="secao form-grade">
        <FormRenomear nome={processo.nome} aoSalvar={renomear} />
        <form className="form-linha" onSubmit={carregarLog}>
          <label className="campo">Log de eventos (.xes)<input className="field" type="file" name="arquivo" accept=".xes" required /></label>
          <button className="btn btn-primary">Carregar</button>
        </form>
      </section>
      {atividades.length > 0 && (
        <>
          <section className="secao"><h2>Grafo do processo</h2><div ref={grafo} /></section>
          <section className="secao">
            <h2>Variantes</h2>
            <Tabela colunas={["#", "SEQUÊNCIA", "TRACES"]} linhas={variantes.slice(0, 10)}>
              {(v) => <tr key={v.numero}><td className="num">{v.numero}</td><td>{v.descricao}</td><td className="num">{v.totalTraces}</td></tr>}
            </Tabela>
          </section>
          <section className="secao">
            <h2>Gerar análise de desvios</h2>
            <form className="form-linha" onSubmit={gerarAnalise}>
              <label className="campo">Atividade
                <select className="field" value={atividade} onChange={(e) => setAtividade(e.target.value)}>
                  {atividades.map((a) => <option key={a.atividade}>{a.atividade}</option>)}
                </select>
              </label>
              <label className="campo">δ do ADWIN<input className="field" value={delta} onChange={(e) => setDelta(e.target.value)} /></label>
              <button className="btn btn-primary">Gerar análise de desvios</button>
            </form>
          </section>
        </>
      )}
      <section className="secao">
        <h2>Análises</h2>
        <Tabela colunas={["NOME", "DESVIOS"]} linhas={analises} vazio="Nenhuma análise ainda.">
          {(a) => <tr key={a.id}><td><Link to={"/analises/" + a.id}>{a.nome}</Link></td><td className="num">{a.drifts.length}</td></tr>}
        </Tabela>
      </section>
    </>
  );
}
