import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";
import { BotaoExcluir, Tabela } from "../componentes";

export default function Processos() {
  const [processos, setProcessos] = useState([]);
  const [nome, setNome] = useState("");
  const navegar = useNavigate();
  const carregar = () => api("GET", "/processos").then(setProcessos);
  useEffect(() => { carregar(); }, []);

  const criar = async (e) => {
    e.preventDefault();
    const processo = await api("POST", "/processos", { nome });
    navegar("/processos/" + processo.id);
  };
  const excluir = async (id) => { await api("DELETE", "/processos/" + id); carregar(); };

  return (
    <>
      <div className="page-head"><h1>Processos</h1></div>
      <section className="secao">
        <form className="form-linha" onSubmit={criar}>
          <label className="campo">Novo processo<input className="field" value={nome} onChange={(e) => setNome(e.target.value)} required /></label>
          <button className="btn btn-primary">Criar processo</button>
        </form>
      </section>
      <section className="secao">
        <Tabela colunas={["NOME", "LOG", "TRACES", ""]} linhas={processos} vazio="Nenhum processo ainda.">
          {(p) => (
            <tr key={p.id}>
              <td><Link to={"/processos/" + p.id}>{p.nome}</Link></td><td className="mono">{p.arquivo || "—"}</td>
              <td className="num">{p.totalTraces}</td><td className="acoes"><BotaoExcluir aoExcluir={() => excluir(p.id)} /></td>
            </tr>
          )}
        </Tabela>
      </section>
    </>
  );
}
