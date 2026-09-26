/**
 * dom.js
 * Camada responsável EXCLUSIVAMENTE pela manipulação do DOM.
 * Não faz chamadas de rede — apenas lê/escreve na interface.
 * Recebe dados prontos e devolve elementos/valores; a orquestração
 * (o que fazer com cada evento) fica a cargo de app.js.
 */

// --- Referências dos elementos (cache único, evita repetir querySelector) ---
export const elementos = {
    form: document.getElementById("form-cliente"),
    inputId: document.getElementById("cliente-id"),
    inputNome: document.getElementById("nome"),
    inputEmail: document.getElementById("email"),
    inputTelefone: document.getElementById("telefone"),
    inputCidade: document.getElementById("cidade"),
    btnSalvar: document.getElementById("btn-salvar"),
    btnCancelar: document.getElementById("btn-cancelar"),
    btnAtualizar: document.getElementById("btn-atualizar"),
    mensagemStatus: document.getElementById("mensagem-status"),
    corpoTabela: document.getElementById("corpo-tabela-clientes"),
    tabelaVazia: document.getElementById("tabela-vazia"),
};

/** Lê os dados atualmente preenchidos no formulário. */
export function obterDadosFormulario() {
    return {
        id: elementos.inputId.value ? Number(elementos.inputId.value) : null,
        nome: elementos.inputNome.value.trim(),
        email: elementos.inputEmail.value.trim(),
        telefone: elementos.inputTelefone.value.trim(),
        cidade: elementos.inputCidade.value.trim(),
    };
}

/** Limpa o formulário e sai do modo de edição. */
export function limparFormulario() {
    elementos.form.reset();
    elementos.inputId.value = "";
    elementos.btnCancelar.hidden = true;
    elementos.btnSalvar.textContent = "Salvar";
    limparErrosFormulario();
    reiniciarRevelacaoProgressiva();
}

/**
 * Revela o próximo campo do formulário (usado quando o campo anterior é
 * preenchido corretamente). Move o foco para o novo campo, o que ajuda
 * tanto quem navega por teclado quanto quem usa leitor de tela.
 * @param {number} numeroPasso - valor de data-step do bloco a revelar
 */
export function revelarProximoCampo(numeroPasso) {
    const proximoBloco = document.querySelector(`[data-step="${numeroPasso}"]`);
    if (!proximoBloco || !proximoBloco.hidden) return;

    proximoBloco.hidden = false;
    atualizarProgresso(numeroPasso);

    const primeiroInput = proximoBloco.querySelector("input");
    if (primeiroInput) {
        primeiroInput.focus();
    }
}

/**
 * Mostra todos os campos de uma vez (usado no modo de edição: como os
 * dados já existem e são válidos, não faz sentido pedir para o usuário
 * "desbloquear" cada campo de novo).
 */
export function mostrarTodosOsCampos() {
    document.querySelectorAll("#form-cliente [data-step]").forEach((bloco) => {
        bloco.hidden = false;
    });
    const elementoProgresso = document.getElementById("progresso-formulario");
    if (elementoProgresso) {
        elementoProgresso.textContent = "Todos os campos disponíveis para edição";
    }
}

/** Volta o formulário ao estado inicial: só o campo Nome visível. */
export function reiniciarRevelacaoProgressiva() {
    document.querySelectorAll("#form-cliente [data-step]").forEach((bloco) => {
        bloco.hidden = Number(bloco.dataset.step) !== 1;
    });
    atualizarProgresso(1);
}

/** Atualiza o texto "Passo X de 4" de forma acessível (aria-live já está no HTML). */
function atualizarProgresso(passoAtual) {
    const TOTAL_CAMPOS = 4; // não conta o bloco de botões (step 5)
    const elementoProgresso = document.getElementById("progresso-formulario");
    if (!elementoProgresso) return;

    const passoExibido = Math.min(passoAtual, TOTAL_CAMPOS);
    elementoProgresso.textContent = `Passo ${passoExibido} de ${TOTAL_CAMPOS}`;
}

/** Preenche o formulário com os dados de um cliente para edição. */
export function preencherFormularioParaEdicao(cliente) {
    mostrarTodosOsCampos();
    elementos.inputId.value = cliente.id;
    elementos.inputNome.value = cliente.nome;
    elementos.inputEmail.value = cliente.email;
    elementos.inputTelefone.value = cliente.telefone;
    elementos.inputCidade.value = cliente.cidade;
    elementos.btnCancelar.hidden = false;
    elementos.btnSalvar.textContent = "Atualizar";
    elementos.inputNome.focus();
}

/** Exibe uma mensagem de erro abaixo de um campo específico. */
export function exibirErroCampo(nomeCampo, mensagem) {
    const campoErro = document.getElementById(`erro-${nomeCampo}`);
    const input = document.getElementById(nomeCampo);
    if (campoErro) campoErro.textContent = mensagem;
    if (input) input.classList.add("invalido");
}

/** Remove todas as mensagens de erro de validação do formulário. */
export function limparErrosFormulario() {
    document.querySelectorAll(".erro").forEach((el) => (el.textContent = ""));
    document.querySelectorAll(".campo input").forEach((el) => el.classList.remove("invalido"));
}

/**
 * Exibe uma mensagem de status geral (sucesso ou erro) acima da tabela.
 * @param {string} texto
 * @param {"sucesso"|"erro"} tipo
 */
export function exibirMensagemStatus(texto, tipo = "sucesso") {
    elementos.mensagemStatus.textContent = texto;
    elementos.mensagemStatus.className = `mensagem-status ${tipo}`;

    if (texto) {
        setTimeout(() => {
            elementos.mensagemStatus.textContent = "";
            elementos.mensagemStatus.className = "mensagem-status";
        }, 4000);
    }
}

/**
 * Renderiza a tabela de clientes a partir de uma lista de objetos.
 * @param {Array<object>} clientes
 * @param {{onEditar: Function, onExcluir: Function}} callbacks
 */
export function renderizarTabela(clientes, { onEditar, onExcluir }) {
    elementos.corpoTabela.innerHTML = "";

    if (!clientes || clientes.length === 0) {
        elementos.tabelaVazia.hidden = false;
        return;
    }

    elementos.tabelaVazia.hidden = true;

    const fragmento = document.createDocumentFragment();

    clientes.forEach((cliente) => {
        const linha = document.createElement("tr");

        linha.innerHTML = `
            <td>${escaparHtml(cliente.nome)}</td>
            <td>${escaparHtml(cliente.email)}</td>
            <td>${escaparHtml(cliente.telefone)}</td>
            <td>${escaparHtml(cliente.cidade)}</td>
            <td class="celula-acoes">
                <button type="button" class="botao botao-editar" data-acao="editar">Editar</button>
                <button type="button" class="botao botao-perigo" data-acao="excluir">Excluir</button>
            </td>
        `;

        linha.querySelector('[data-acao="editar"]').addEventListener("click", () => onEditar(cliente));
        linha.querySelector('[data-acao="excluir"]').addEventListener("click", () => onExcluir(cliente));

        fragmento.appendChild(linha);
    });

    elementos.corpoTabela.appendChild(fragmento);
}

/** Previne XSS simples ao inserir texto dinâmico via innerHTML. */
function escaparHtml(texto) {
    const div = document.createElement("div");
    div.textContent = texto ?? "";
    return div.innerHTML;
}