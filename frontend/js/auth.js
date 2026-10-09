const API_BASE_URL = "http://127.0.0.1:8000";
const CHAVE_TOKEN = "access_token";
const URL_LOGIN = "login.html";

export function salvarToken(token) {
    sessionStorage.setItem(CHAVE_TOKEN, token);
}

export function obterToken() {
    return sessionStorage.getItem(CHAVE_TOKEN);
}

export function limparSessaoERedirecionar() {
    sessionStorage.removeItem(CHAVE_TOKEN);
    window.location.href = URL_LOGIN;
}

export function exigirAutenticacao() {
    if (!obterToken()) {
        window.location.href = URL_LOGIN;
        return false;
    }
    return true;
}

export async function validarSessaoNoServidor() {
    try {
        const resposta = await fetchAutenticado(`${API_BASE_URL}/auth/me`);
        return resposta.ok;
    } catch {
        return false;
    }
}

export async function fetchAutenticado(url, opcoes = {}) {
    const token = obterToken();

    const cabecalhos = {
        ...(opcoes.headers || {}),
        Authorization: `Bearer ${token}`,
    };

    const resposta = await fetch(url, { ...opcoes, headers: cabecalhos });

    if (resposta.status === 401 || resposta.status === 403) {
        limparSessaoERedirecionar();
        throw new Error("Sessão expirada. Faça login novamente.");
    }

    return resposta;
}