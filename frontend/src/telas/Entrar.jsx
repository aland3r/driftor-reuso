import { useNavigate } from "react-router-dom";

const PASSOS = [
  ["Envie o log", "Arquivo .xes da produção. As atividades e o grafo do processo aparecem na hora."],
  ["Encontre o desvio", "O ADWIN lê a série de durações e marca onde o processo mudou de patamar."],
  ["Dispare a manutenção", "O gestor manda o técnico verificar; o técnico executa e registra o que fez."],
];

// Landing com a entrada simulada: o papel escolhido fica guardado e vai em toda chamada à API.
export default function Entrar({ papeis }) {
  const navegar = useNavigate();
  const entrar = (chave) => { localStorage.setItem("papel", chave); navegar(papeis[chave].inicio); };
  return (
    <div className="landing">
      <section className="hero">
        <div>
          <h1>Veja quando o seu processo mudou de ritmo.</h1>
          <p>O Driftor lê o log de eventos, desenha o processo como um grafo e aponta, na série de durações, onde o desempenho mudou. Cada desvio pode virar uma ordem de manutenção.</p>
          <div className="perfis">
            <p className="label">ENTRAR COMO (SEM SENHA)</p>
            {Object.entries(papeis).sort().map(([chave, p]) => (
              <button key={chave} className="perfil-cartao" onClick={() => entrar(chave)}><strong>{p.nome}</strong><span className="seta">→</span></button>
            ))}
          </div>
        </div>
        <ArteDoDesvio />
      </section>
      <section className="passos">
        {PASSOS.map(([titulo, texto], i) => (
          <div key={titulo}><span className="passo">{i + 1}</span><h2>{titulo}</h2><p>{texto}</p></div>
        ))}
      </section>
      <footer className="rodape">Alander Menezes Arantes de Ávila · Emanuelle Skolut Jose · PUCPR, 2026</footer>
    </div>
  );
}

function ArteDoDesvio() {
  const pontos = [62, 60, 64, 61, 63, 59, 62, 60, 61, 63, 60, 62, 44, 41, 43, 40, 42, 44, 41, 43, 40, 42, 41, 43, 42, 40];
  const x = (i) => 24 + i * 16;
  const y = (v) => 180 - v * 2;
  return (
    <svg className="arte" viewBox="0 0 440 240" role="img" aria-label="Série de durações com um desvio marcado">
      <line x1={x(12)} x2={x(12)} y1="36" y2="204" stroke="#dc2626" strokeDasharray="5 3" />
      <text x={x(12) + 6} y="50" fontSize="12" fill="#fca5a5">desvio</text>
      <path d={pontos.map((v, i) => `${i ? "L" : "M"}${x(i)},${y(v)}`).join(" ")} fill="none" stroke="#4d8fc0" strokeWidth="2.2" />
      {pontos.map((v, i) => <circle key={i} cx={x(i)} cy={y(v)} r={i === 12 ? 4.5 : 2.4} fill={i === 12 ? "#f59e0b" : "#c8e2f5"} />)}
    </svg>
  );
}
