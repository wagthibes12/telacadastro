import { autenticar } from "./auth-api.js";
import { salvarToken } from "./auth.js";

const elementos = {
    form: document.getElementById("form-login"),
    inputEmail: document.getElementById("login-email"),
    inputSenha: document.getElementById("login-senha"),
    btnEntrar: document.getElementById("btn-entrar"),
    mensagemLogin: document.getElementById("mensagem-login"),
    erroEmail: document.getElementById("erro-login-email"),
    erroSenha: document.getElementById("erro-login-senha"),
    btnMostrarSenha: document.getElementById("btn-mostrar-senha"),
    iconeOlho: document.getElementById("icone-olho"),
};

function limparMensagens() {
    elementos.erroEmail.textContent = "";
    elementos.erroSenha.textContent = "";
    elementos.mensagemLogin.textContent = "";
    elementos.mensagemLogin.className = "mensagem-status";
}

function exibirMensagem(texto, tipo) {
    elementos.mensagemLogin.textContent = texto;
    elementos.mensagemLogin.className = `mensagem-status ${tipo}`;
}

async function tratarEnvioLogin(evento) {
    evento.preventDefault();
    limparMensagens();

    const credenciais = {
        email: elementos.inputEmail.value.trim(),
        senha: elementos.inputSenha.value,
    };

    elementos.btnEntrar.disabled = true;

    try {
        const resultado = await autenticar(credenciais);

        // Guarda o token SÓ no sessionStorage desta aba
        salvarToken(resultado.access_token);

        exibirMensagem("Login realizado! Redirecionando...", "sucesso");
        window.location.href = "index.html";
    } catch (erro) {
        exibirMensagem(erro.message, "erro");
    } finally {
        elementos.btnEntrar.disabled = false;
    }
}

const ICONE_OLHO_ABERTO = `
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8Z"></path>
    <circle cx="12" cy="12" r="3"></circle>
`;

const ICONE_OLHO_FECHADO = `
    <path d="M17.94 17.94A10.94 10.94 0 0 1 12 20c-7 0-11-8-11-8a18.5 18.5 0 0 1 5.06-5.94"></path>
    <path d="M9.9 4.24A10.94 10.94 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"></path>
    <path d="M14.12 14.12a3 3 0 1 1-4.24-4.24"></path>
    <path d="M1 1l22 22"></path>
`;

function alternarVisibilidadeSenha() {
    const estaVisivel = elementos.inputSenha.type === "text";
    elementos.inputSenha.type = estaVisivel ? "password" : "text";
    elementos.btnMostrarSenha.setAttribute("aria-pressed", String(!estaVisivel));
    elementos.btnMostrarSenha.setAttribute(
        "aria-label",
        estaVisivel ? "Mostrar senha" : "Ocultar senha"
    );
    elementos.iconeOlho.innerHTML = estaVisivel ? ICONE_OLHO_ABERTO : ICONE_OLHO_FECHADO;
}

function iniciar() {
    elementos.form.addEventListener("submit", tratarEnvioLogin);
    elementos.form.addEventListener("submit", tratarEnvioLogin);
    elementos.btnMostrarSenha.addEventListener("click", alternarVisibilidadeSenha);
}

document.addEventListener("DOMContentLoaded", iniciar);