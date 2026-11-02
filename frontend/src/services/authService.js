/**
 * authService — chamadas HTTP de autenticação da API Simple Mark
 *
 * Login em DUAS etapas (definido pelo backend):
 *   1) POST /api/v1/auth/login           { identificador, senha }   -> { id_desafio, email_mascarado, expira_em_segundos, mensagem }
 *   2) POST /api/v1/auth/login/confirmar { id_desafio, codigo }     -> { access_token, token_type, usuario }
 *   GET  /api/v1/auth/eu    (Bearer)  -> dados da conta logada
 *   POST /api/v1/auth/sair  (Bearer)  -> 204, encerra a sessão
 *
 * Erros da API chegam como { "mensagem": "..." } (já em português).
 * Aqui eles viram `ApiError`, e `error.message` pode ser exibido direto na tela.
 *
 * URL base: variável VITE_API_URL do arquivo `.env` do frontend.
 */

const BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8080').replace(/\/$/, '')
const PREFIXO = '/api/v1'

export class ApiError extends Error {
  constructor(message, status = 0) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function requisitar(caminho, { method = 'GET', body, token } = {}) {
  const headers = { Accept: 'application/json' }
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (token) headers.Authorization = `Bearer ${token}`

  let resposta
  try {
    resposta = await fetch(`${BASE_URL}${PREFIXO}${caminho}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  } catch {
    throw new ApiError('Não foi possível conectar ao servidor. Verifique se a API está no ar e tente novamente.')
  }

  if (resposta.status === 204) return null

  let dados = null
  try {
    dados = await resposta.json()
  } catch {
    // resposta sem JSON
  }

  if (!resposta.ok) {
    const mensagem =
      (dados && typeof dados.mensagem === 'string' && dados.mensagem) ||
      (dados && typeof dados.detail === 'string' && dados.detail) ||
      'Não foi possível concluir a solicitação. Tente novamente.'
    throw new ApiError(mensagem, resposta.status)
  }
  return dados
}

/** Etapa 1: confere e-mail/CPF + senha e dispara o código por e-mail. */
export function iniciarLogin({ identificador, senha }) {
  return requisitar('/auth/login', { method: 'POST', body: { identificador, senha } })
}

/** Etapa 2: confere o código de 6 dígitos e devolve { access_token, token_type, usuario }. */
export function confirmarLogin({ idDesafio, codigo }) {
  return requisitar('/auth/login/confirmar', {
    method: 'POST',
    body: { id_desafio: idDesafio, codigo },
  })
}

/** Dados da conta dona do token. */
export function obterUsuario(token) {
  return requisitar('/auth/eu', { token })
}

/** Encerra a sessão no servidor. */
export function sair(token) {
  return requisitar('/auth/sair', { method: 'POST', token })
}


/** Cadastra um novo paciente. */
export function cadastrarPaciente(dados) {
  return requisitar('/cadastro/paciente', {
    method: 'POST',
    body: dados,
  })
}

/** * Cadastra um novo profissional. */
export function cadastrarProfissional(dados) {
  return requisitar('/cadastro/profissional', {
    method: 'POST',
    body: dados,
  })
}
