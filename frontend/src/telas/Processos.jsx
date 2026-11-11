import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";
import { BotaoExcluir, Tabela } from "../componentes";

// Tela inicial do gestor: os processos em cartões e as manutenções com o status.
export default function Processos() {
  const [processos, setProcessos] = useState([]);
  const [manutencoes, setManutencoes] = useState([]);
  const [nome, setNome] = useState("");
  const navegar = useNavigate();
  const carregar = () => api("GET", "/processos").then(setProcessos);
  useEffect(() => { carregar(); api("GET", "/manutencoes").then(setManutencoes); }, []);

  const criar = async (e) => {
    e.preventDefault();
    const processo = await api("POST", "/processos", { nome });
    navegar("/processos/" + processo.id);
  };
  const excluir = async (id) => { await api("DELETE", "/processos/" + id); carregar(); };
  const aguardando = manutencoes.filter((m) => m.status === "pendente").length;

  return (
    <>
      <div className="page-head">
        <div><h1>Processos e manutenções</h1><p>Crie um processo e carregue o log; a partir dele, gere análises e dispare manutenções.</p></div>
        <form className="form-linha" onSubmit={criar}>
          <input className="field" placeholder="Nome do novo processo" value={nome} onChange={(e) => setNome(e.target.value)} required />
          <button className="btn btn-primary">Criar processo</button>
        </form>
      </div>
      <div className="numeros">
        <div><b>{processos.length}</b>processos</div>
        <div><b className="aguardando">{aguardando}</b>manutenções aguardando</div>
        <div><b className="ok">{manutencoes.length - aguardando}</b>manutenções feitas</div>
      </div>
      <ul className="cartoes">
        {processos.map((p) => (
          <li key={p.id} className="cartao">
            <Link to={"/processos/" + p.id}>
              <svg className="miniatura" viewBox="0 0 120 40" aria-hidden="true">
                {[10, 40, 70, 100].map((x, i) => <rect key={x} x={x - 8} y="15" width="16" height="10" rx="2" className={i % 3 ? "" : "forte"} />)}
                <path d="M18 20H32M48 20H62M78 20H92" />
              </svg>
              <strong>{p.nome}</strong>
              <span>{p.arquivo ? `${p.totalTraces} traces · ${p.totalEventos} eventos` : "Sem log de eventos"}</span>
            </Link>
            <BotaoExcluir aoExcluir={() => excluir(p.id)} />
          </li>
        ))}
        {processos.length === 0 && <li className="vazio">Nenhum processo ainda. Crie o primeiro acima.</li>}
      </ul>
      <section className="secao">
        <h2>Manutenções</h2>
        <Tabela colunas={["DESCRIÇÃO", "PROCESSO · ANÁLISE", "DESVIO", "STATUS"]} linhas={manutencoes} vazio="Nenhuma manutenção disparada ainda.">
          {(m) => (
            <tr key={m.id}>
              <td><Link to={"/manutencoes/" + m.id}>{m.descricao}</Link></td><td>{m.processo} · {m.analise}</td>
              <td className="num">{m.desvio}</td><td><Status valor={m.status} /></td>
            </tr>
          )}
        </Tabela>
      </section>
    </>
  );
}

export function Status({ valor }) {
  return valor === "pendente" ? <span className="selo aguardando">Aguardando técnico</span> : <span className="selo ok">✓ Concluída</span>;
}
