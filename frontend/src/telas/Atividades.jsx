import { useEffect, useState } from "react";
import { api } from "../api";
import { BotaoExcluir, Tabela } from "../componentes";

export default function Atividades() {
  const [atividades, setAtividades] = useState([]);
  const [nome, setNome] = useState("");
  const carregar = () => api("GET", "/atividades").then(setAtividades);
  useEffect(() => { carregar(); }, []);

  const criar = async (e) => {
    e.preventDefault();
    await api("POST", "/atividades", { nome });
    setNome("");
    carregar();
  };
  const renomear = async (e, id) => {
    e.preventDefault();
    await api("PUT", "/atividades/" + id,  // vai para o AtividadeController (PUT); api() manda o papel no cabeçalho
      Object.fromEntries(new FormData(e.target)));
    carregar();
  };
  const excluir = async (id) => { await api("DELETE", "/atividades/" + id); carregar(); };

  return (
    <>
      <div className="page-head"><div><h1>Atividades</h1><p>O upload do log cria uma atividade para cada nome novo.</p></div></div>
      <section className="secao">
        <form className="form-linha" onSubmit={criar}>
          <label className="campo">Nome<input className="field" value={nome} onChange={(e) => setNome(e.target.value)} required /></label>
          <button className="btn btn-primary">Criar atividade</button>
        </form>
      </section>
      <section className="secao">
        <Tabela colunas={["NOME", ""]} linhas={atividades} vazio="Nenhuma atividade ainda.">
          {(a) => (
            <tr key={a.id}>
              <td>
                <form className="form-linha" onSubmit={(e) => renomear(e, a.id)}>
                  <input className="field" name="nome" defaultValue={a.nome} />
                  <button className="btn btn-sm">Renomear</button>
                </form>
              </td>
              <td className="acoes"><BotaoExcluir aoExcluir={() => excluir(a.id)} /></td>
            </tr>
          )}
        </Tabela>
      </section>
    </>
  );
}
