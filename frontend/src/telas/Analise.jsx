import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api, papel } from "../api";
import { BotaoExcluir, FormRenomear, Tabela } from "../componentes";

export default function Analise() {
  const { id } = useParams();
  const [dados, setDados] = useState(null);
  const [descricao, setDescricao] = useState("");
  const navegar = useNavigate();
  const carregar = () => api("GET", "/analises/" + id).then(setDados);
  useEffect(() => { carregar(); }, [id]);
  if (!dados) return null;
  const { analise, processo, serie, manutencoes } = dados;
  const gestor = papel() === "gestor";  // VARIABILIDADE: o técnico só vê

  const renomear = async (nome) => { await api("PUT", "/analises/" + id, { nome }); carregar(); };
  const excluir = async () => { await api("DELETE", "/analises/" + id); navegar("/processos/" + processo.id); };
  const disparar = async (driftId) => {
    await api("POST", `/analises/${id}/manutencoes`, { driftId, descricao });
    setDescricao("");
    carregar();
  };

  const maior = Math.max(...serie), menor = Math.min(...serie);
  const x = (i) => (i * 900) / (serie.length - 1);
  const y = (v) => 230 - ((v - menor) * 220) / (maior - menor || 1);

  return (
    <>
      <div className="page-head">
        <div><h1>{analise.nome}</h1><div className="meta">Processo {processo.nome} · δ {analise.delta} · {analise.totalObservacoes} observações</div></div>
        {gestor && <BotaoExcluir aoExcluir={excluir} rotulo="Excluir análise" />}
      </div>
      {gestor && <section className="secao"><FormRenomear nome={analise.nome} aoSalvar={renomear} /></section>}
      <section className="secao">
        <h2>Série analisada</h2>
        <svg className="grafico" viewBox="0 0 900 240" preserveAspectRatio="none">
          <polyline points={serie.map((v, i) => `${x(i)},${y(v)}`).join(" ")} />
          {analise.drifts.map((d) => <line key={d.id} x1={x(d.inicio)} x2={x(d.inicio)} y1="0" y2="240" />)}
        </svg>
      </section>
      <section className="secao">
        <h2>Desvios encontrados ({analise.drifts.length})</h2>
        {gestor && <input className="field" placeholder="O que o técnico deve verificar" value={descricao} onChange={(e) => setDescricao(e.target.value)} />}
        <Tabela colunas={["#", "RESUMO", ""]} linhas={analise.drifts} vazio="Nenhum desvio: o processo ficou estável.">
          {(d) => (
            <tr key={d.id}>
              <td className="num">{d.posicao}</td><td>{d.resumo}</td>
              <td className="acoes">{gestor && (manutencoes.some((m) => m.drift_id === d.id)
                ? <span className="ok">✓ Manutenção disparada</span>
                : <button className="btn btn-sm" onClick={() => disparar(d.id)}>Disparar manutenção</button>)}</td>
            </tr>
          )}
        </Tabela>
      </section>
      <section className="secao">
        <h2>Manutenções desta análise</h2>
        <Tabela colunas={["DESCRIÇÃO", "DESVIO", "STATUS"]} linhas={manutencoes} vazio="Nenhuma manutenção disparada.">
          {(m) => <tr key={m.id}><td><Link to={"/manutencoes/" + m.id}>{m.descricao}</Link></td><td className="num">{m.desvio}</td><td>{m.status}</td></tr>}
        </Tabela>
      </section>
    </>
  );
}
