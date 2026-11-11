// COMPACTAÇÃO no front: pedaços de tela que se repetiam nos CRUDs.
import { useState } from "react";

export function BotaoExcluir({ aoExcluir, rotulo = "Excluir" }) {
  return <button className="btn btn-sm" onClick={aoExcluir}>{rotulo}</button>;
}

export function FormRenomear({ nome, aoSalvar }) {
  const [novo, setNovo] = useState(nome);
  return (
    <form className="form-linha" onSubmit={(e) => { e.preventDefault(); aoSalvar(novo); }}>
      <label className="campo">Nome<input className="field" value={novo} onChange={(e) => setNovo(e.target.value)} /></label>
      <button className="btn">Renomear</button>
    </form>
  );
}

export function Tabela({ colunas, linhas, vazio, children }) {
  return (
    <table className="tabela">
      <thead><tr>{colunas.map((c) => <th key={c}>{c}</th>)}</tr></thead>
      <tbody>{linhas.length ? linhas.map(children) : <tr><td colSpan={colunas.length} className="vazio">{vazio}</td></tr>}</tbody>
    </table>
  );
}
