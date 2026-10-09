/**
 * api.js
 * Camada responsável EXCLUSIVAMENTE pela comunicação com o backend (Fetch API).
 * Não manipula o DOM — apenas envia/recebe dados. Isso permite reutilizar
 * este módulo em qualquer outra interface (ex: um app mobile) sem alterações.
 */
import { fetchAutenticado } from "./auth.js";


const API_BASE_URL = "http://127.0.0.1:8000";

/**
 * Trata a resposta HTTP de forma centralizada, lançando um erro legível
 * quando a API retorna um status de falha (4xx/5xx).
 * @param {Response} resposta
 */
async function tratarResposta(resposta) {
    if (resposta.status === 204) {
        return null; // Sem conteúdo (ex.: DELETE bem-sucedido)
    }

    const dados = await resposta.json().catch(() => null);

    if (!resposta.ok) {
        const mensagem =
            dados?.detail ||
            `Erro inesperado (HTTP ${resposta.status}) ao comunicar com o servidor.`;
        throw new Error(mensagem);
    }

    return dados;
}

/** Busca todos os clientes cadastrados. */
export async function buscarClientes() {
    const resposta = await fetchAutenticado(`${API_BASE_URL}/clientes`);
    return tratarResposta(resposta);
}

/**
 * Cria um novo cliente.
 * @param {{nome: string, email: string, telefone: string, cidade: string}} cliente
 */
export async function criarCliente(cliente) {
    const resposta = await fetchAutenticado(`${API_BASE_URL}/clientes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(cliente),
    });
    return tratarResposta(resposta);
}

/**
 * Atualiza um cliente existente.
 * @param {number} id
 * @param {{nome: string, email: string, telefone: string, cidade: string}} cliente
 */
export async function atualizarCliente(id, cliente) {
    const resposta = await fetchAutenticado(`${API_BASE_URL}/clientes/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(cliente),
    });
    return tratarResposta(resposta);
}

/**
 * Remove um cliente pelo ID.
 * @param {number} id
 */
export async function deletarCliente(id) {
    const resposta = await fetchAutenticado(`${API_BASE_URL}/clientes/${id}`, {
        method: "DELETE",
    });
    return tratarResposta(resposta);
}
