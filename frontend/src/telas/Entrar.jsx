import { useNavigate } from "react-router-dom";

// Entrada simulada: o papel escolhido fica guardado e vai em toda chamada à API.
export default function Entrar({ papeis }) {
  const navegar = useNavigate();
  const entrar = (chave) => { localStorage.setItem("papel", chave); navegar(papeis[chave].inicio); };
  return (
    <section className="entrada">
      <div><h1>Do desvio no processo à manutenção na máquina.</h1></div>
      <div className="perfis">
        <p className="label">ENTRAR COMO (SEM SENHA)</p>
        {Object.entries(papeis).map(([chave, p]) => (
          <button key={chave} className="perfil-cartao" onClick={() => entrar(chave)}><strong>{p.nome}</strong><span className="seta">→</span></button>
        ))}
      </div>
    </section>
  );
}
