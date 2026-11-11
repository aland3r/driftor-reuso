import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, papel } from "../api";
import { BotaoExcluir, Tabela } from "../componentes";
import { Status } from "./Processos";

export default function Manutencoes() {
  const [manutencoes, setManutencoes] = useState([]);
  const carregar = () => api("GET", "/manutencoes").then(setManutencoes);
  useEffect(() => { carregar(); }, []);
  const excluir = async (id) => { await api("DELETE", "/manutencoes/" + id); carregar(); };

  return (
    <>
      <div className="page-head"><h1>Manutenções</h1></div>
      <section className="secao">
        <Tabela colunas={["DESCRIÇÃO", "ANÁLISE", "DESVIO", "STATUS", ""]} linhas={manutencoes} vazio="Nenhuma manutenção disparada ainda.">
          {(m) => (
            <tr key={m.id}>
              <td><Link to={"/manutencoes/" + m.id}>{m.descricao}</Link></td><td>{m.analise}</td>
              <td className="num">{m.desvio}</td><td><Status valor={m.status} /></td>
              {/* VARIABILIDADE: o técnico executa, o gestor exclui */}
              <td className="acoes">
                {papel() === "tecnico" && m.status === "pendente" && <Link className="btn btn-sm btn-primary" to={"/manutencoes/" + m.id}>Executar</Link>}
                {papel() === "gestor" && <BotaoExcluir aoExcluir={() => excluir(m.id)} />}
              </td>
            </tr>
          )}
        </Tabela>
      </section>
    </>
  );
}
