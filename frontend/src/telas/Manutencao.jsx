import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, papel } from "../api";

export default function Manutencao() {
  const { id } = useParams();
  const [dados, setDados] = useState(null);
  const [observacoes, setObservacoes] = useState("");
  const carregar = () => api("GET", "/manutencoes/" + id).then(setDados);
  useEffect(() => { carregar(); }, [id]);
  if (!dados) return null;
  const { manutencao, analise } = dados;

  const concluir = async (e) => {
    e.preventDefault();
    await api("PUT", `/manutencoes/${id}/concluir`, { observacoes });
    carregar();
  };

  return (
    <>
      <div className="page-head">
        <div><h1>{manutencao.descricao}</h1><div className="meta">{manutencao.status} · Análise <Link to={"/analises/" + analise.id}>{analise.nome}</Link></div></div>
      </div>
      {/* VARIABILIDADE: só o técnico conclui */}
      {manutencao.status === "pendente" && papel() === "tecnico" ? (
        <section className="secao">
          <form className="form-linha" onSubmit={concluir}>
            <label className="campo">Observações do que foi feito<input className="field" value={observacoes} onChange={(e) => setObservacoes(e.target.value)} required /></label>
            <button className="btn btn-primary">Marcar como concluída</button>
          </form>
        </section>
      ) : (
        <section className="secao"><h2>Observações do técnico</h2><p>{manutencao.observacoes || "Aguardando o técnico."}</p></section>
      )}
    </>
  );
}
