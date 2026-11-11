// Toda chamada ao backend leva o papel escolhido na entrada (cabeçalho "Papel").
export const papel = () => localStorage.getItem("papel");

export async function api(metodo, url, corpo) {
  const opcoes = { method: metodo, headers: { Papel: papel() } };
  if (corpo instanceof FormData) opcoes.body = corpo;
  else if (corpo) {
    opcoes.headers["Content-Type"] = "application/json";
    opcoes.body = JSON.stringify(corpo);
  }
  const resposta = await fetch("/api" + url, opcoes);
  const texto = await resposta.text();
  return texto ? JSON.parse(texto) : null;
}
