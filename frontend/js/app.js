/**
 * app.js
 * Ponto de entrada do frontend. Orquestra a interação entre:
 *   - api.js   -> comunicação com o backend
 *   - dom.js   -> leitura/escrita na interface
 * Não deve conter lógica de fetch nem manipulação direta de elementos além
 * do necessário para registrar os event listeners.
 */

import { buscarClientes, criarCliente, atualizarCliente, deletarCliente } from "./api.js";
import {
    elementos,
    obterDadosFormulario,
    limparFormulario,
    preencherFormularioParaEdicao,
    exibirErroCampo,
    limparErrosFormulario,
    exibirMensagemStatus,
    renderizarTabela,
    revelarProximoCampo,
} from "./dom.js";

/** Carrega a lista de clientes do backend e atualiza a tabela na tela. */
async function carregarClientes() {
    try {
        const clientes = await buscarClientes();
        renderizarTabela(clientes, {
            onEditar: iniciarEdicaoCliente,
            onExcluir: confirmarExclusaoCliente,
        });
    } catch (erro) {
        exibirMensagemStatus(`Não foi possível carregar os clientes: ${erro.message}`, "erro");
    }
}

/** Coloca o formulário em modo de edição para o cliente selecionado. */
function iniciarEdicaoCliente(cliente) {
    preencherFormularioParaEdicao(cliente);
}

/** Pede confirmação e exclui o cliente selecionado. */
async function confirmarExclusaoCliente(cliente) {
    const confirmou = window.confirm(`Excluir o cliente "${cliente.nome}"?`);
    if (!confirmou) return;

    try {
        await deletarCliente(cliente.id);
        exibirMensagemStatus("Cliente excluído com sucesso.", "sucesso");
        await carregarClientes();
    } catch (erro) {
        exibirMensagemStatus(`Erro ao excluir cliente: ${erro.message}`, "erro");
    }
}

/** Validação simples no lado do cliente, antes de enviar ao backend. */
function validarFormulario(dados) {
    limparErrosFormulario();
    let valido = true;

    if (dados.nome.length < 2) {
        exibirErroCampo("nome", "Informe ao menos 2 caracteres.");
        valido = false;
    }
    if (!/^\S+@\S+\.\S+$/.test(dados.email)) {
        exibirErroCampo("email", "Informe um e-mail válido.");
        valido = false;
    }
    if (dados.telefone.replace(/\D/g, "").length < 10) {
        exibirErroCampo("telefone", "Informe um telefone válido com DDD.");
        valido = false;
    }
    if (dados.cidade.length < 2) {
        exibirErroCampo("cidade", "Informe ao menos 2 caracteres.");
        valido = false;
    }

    return valido;
}

/** Trata o envio (criação ou atualização) do formulário. */
async function tratarEnvioFormulario(evento) {
    evento.preventDefault();

    const dados = obterDadosFormulario();
    if (!validarFormulario(dados)) return;

    const payload = {
        nome: dados.nome,
        email: dados.email,
        telefone: dados.telefone,
        cidade: dados.cidade,
    };

    elementos.btnSalvar.disabled = true;

    try {
        if (dados.id) {
            await atualizarCliente(dados.id, payload);
            exibirMensagemStatus("Cliente atualizado com sucesso.", "sucesso");
        } else {
            await criarCliente(payload);
            exibirMensagemStatus("Cliente cadastrado com sucesso.", "sucesso");
        }

        limparFormulario();
        await carregarClientes();
    } catch (erro) {
        exibirMensagemStatus(erro.message, "erro");
    } finally {
        elementos.btnSalvar.disabled = false;
    }
}

/** Registra todos os event listeners da aplicação. */
function registrarEventos() {
    elementos.form.addEventListener("submit", tratarEnvioFormulario);
    elementos.btnCancelar.addEventListener("click", limparFormulario);
    elementos.btnAtualizar.addEventListener("click", carregarClientes);
    
    // Chama a função de cascata ao iniciar
    configurarEventosCascata(); 
}

/** Inicialização da aplicação. */
function iniciar() {
    registrarEventos();
    carregarClientes();
}

document.addEventListener("DOMContentLoaded", iniciar);
