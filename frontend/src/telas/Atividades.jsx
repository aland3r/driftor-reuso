import { useEffect, useState } from "react";
import { api } from "../api";
import { BotaoExcluir, Tabela } from "../componentes";

export default function Atividades() {
  const [atividades, setAtividades] = useState([]);
  const [nova, setNova] = useState({ nome: "", descricao: "" });
  const carregar = () => api("GET", "/atividades").then(setAtividades);
  useEffect(() => { carregar(); }, []);

  const criar = async (e) => {
    e.preventDefault();
    await api("POST", "/atividades", nova);
    setNova({ nome: "", descricao: "" });
    carregar();
  };
  const editar = async (e, id) => {
    e.preventDefault();
    await api("PUT", "/atividades/" + id, Object.fromEntries(new FormData(e.target)));
    carregar();
  };
  const excluir = async (id) => { await api("DELETE", "/atividades/" + id); carregar(); };

  return (
    <>
      <div className="page-head"><div><h1>Atividades</h1><p>O upload do log cria uma atividade para cada nome novo.</p></div></div>
      <section className="secao">
        <form className="form-linha" onSubmit={criar}>
          <label className="campo">Nome<input className="field" value={nova.nome} onChange={(e) => setNova({ ...nova, nome: e.target.value })} required /></label>
          <label className="campo">Descrição<input className="field" value={nova.descricao} onChange={(e) => setNova({ ...nova, descricao: e.target.value })} /></label>
          <button className="btn btn-primary">Criar atividade</button>
        </form>
      </section>
      <section className="secao">
        <Tabela colunas={["NOME E DESCRIÇÃO", ""]} linhas={atividades} vazio="Nenhuma atividade ainda.">
          {(a) => (
            <tr key={a.id}>
              <td>
                <form className="form-linha" onSubmit={(e) => editar(e, a.id)}>
                  <input className="field" name="nome" defaultValue={a.nome} />
                  <input className="field" name="descricao" defaultValue={a.descricao} placeholder="Descrição" />
                  <button className="btn btn-sm">Salvar</button>
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
