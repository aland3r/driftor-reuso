import { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { HashRouter, NavLink, Navigate, Route, Routes, useLocation } from "react-router-dom";
import { api, papel } from "./api";
import Entrar from "./telas/Entrar";
import Processos from "./telas/Processos";
import Processo from "./telas/Processo";
import Atividades from "./telas/Atividades";
import Analise from "./telas/Analise";
import Manutencoes from "./telas/Manutencoes";
import Manutencao from "./telas/Manutencao";
import "./estilo.css";

const MENU = [["/processos", "Processos", "processos"], ["/atividades", "Atividades", "atividades"], ["/manutencoes", "Manutenções", "manutencoes"]];

function Layout() {
  const [papeis, setPapeis] = useState(null);
  const [avisos, setAvisos] = useState([]);
  const local = useLocation();
  useEffect(() => { api("GET", "/papeis").then(setPapeis); }, []);
  useEffect(() => { if (papel()) api("GET", "/avisos").then(setAvisos); }, [local]);  // Observer: avisos do papel
  if (!papeis) return null;
  const meu = papeis[papel()];
  return (
    <>
      <header className="app-header">
        <NavLink to="/" className="logo">
          <svg width="28" height="28" viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="8" fill="#202b3a" /><path d="M6 21h6l3-8 4 12 3-6h4" fill="none" stroke="#4d8fc0" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" /><circle cx="19" cy="25" r="2.6" fill="#f59e0b" /></svg>
          <span className="logo-word">Driftor</span>
        </NavLink>
        {/* VARIABILIDADE: o menu mostra só o que o papel pode usar */}
        {meu && <nav className="app-nav">{MENU.filter((m) => meu.pode.includes(m[2])).map(([rota, rotulo]) => <NavLink key={rota} to={rota}>{rotulo}</NavLink>)}</nav>}
        {meu && <div className="app-actions">{meu.nome}<NavLink className="btn btn-sm" to="/entrar">Trocar perfil</NavLink></div>}
      </header>
      <main>
        {avisos.map((a) => <div className="aviso" key={a}>{a}</div>)}
        <Routes>
          <Route path="/" element={<Navigate to={meu ? meu.inicio : "/entrar"} />} />
          <Route path="/entrar" element={<Entrar papeis={papeis} />} />
          <Route path="/processos" element={<Processos />} />
          <Route path="/processos/:id" element={<Processo />} />
          <Route path="/atividades" element={<Atividades />} />
          <Route path="/analises/:id" element={<Analise />} />
          <Route path="/manutencoes" element={<Manutencoes />} />
          <Route path="/manutencoes/:id" element={<Manutencao />} />
        </Routes>
      </main>
    </>
  );
}

createRoot(document.getElementById("raiz")).render(<HashRouter><Layout /></HashRouter>);
