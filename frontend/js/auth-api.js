const API_BASE_URL = "http://127.0.0.1:8000";

function extrairMensagemDeErro(dados, status) {
    if (!dados) return `Erro inesperado (HTTP ${status}).`;
    if (Array.isArray(dados.detail)) {
        return dados.detail.map((item) => item.msg).join(" ");
    }
    if (typeof dados.detail === "string") {
        return dados.detail;
    }
    return `Erro inesperado (HTTP ${status}).`;
}

async function tratarResposta(resposta) {
    const dados = await resposta.json().catch(() => null);
    if (!resposta.ok) {
        throw new Error(extrairMensagemDeErro(dados, resposta.status));
    }
    return dados;
}

export async function autenticar(credenciais) {
    const resposta = await fetch(`${API_BASE_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(credenciais),
    });
    return tratarResposta(resposta);
}