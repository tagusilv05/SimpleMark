/**
 * api — cliente HTTP mínimo para falar com o backend (FastAPI)
 *
 * COMO USAR:
 *
 *   import { api } from '@/services/api'
 *
 *   const especialidades = await api.get('/profissionais/lista-especialidade')
 *   const lista = await api.get('/api/v1/profissionais/busca', { ordenar_por: 'avaliacao' })
 *
 * URL BASE
 *   Vem de VITE_API_URL (arquivo .env do frontend). Sem ela, usa http://localhost:8080,
 *   que é a porta da API no docker compose.
 *
 * AUTENTICAÇÃO
 *   O token da conta logada vem SEMPRE da store de login (useAuthStore) e vai no
 *   cabeçalho Authorization de todas as chamadas. Se o servidor responder 401 a uma
 *   chamada autenticada (sessão encerrada, expirada ou conta banida), a sessão local
 *   é apagada e a guarda de rotas manda o usuário para o login.
 *
 * ERROS
 *   Respostas fora de 2xx lançam um ApiError com `status` e `message`.
 *   `message` já vem em português quando o backend envia `detail`.
 *
 * PARÂMETROS (2º argumento do get)
 *   Objeto simples. Valores null / undefined / '' são ignorados.
 *
 * MÉTODOS
 *   api.get(path, params) · api.post(path, body) · api.put(path, body)
 *   api.patch(path, body) · api.delete(path, { body })  -> devolvem o corpo da resposta
 *   body pode ser um FormData (upload de arquivo). Com { blob: true } devolve um Blob.
 *
 *   O export default (legado) devolve { data } e aceita get(path, { params }).
 */
import { useAuthStore } from '@/stores/auth'

import router from '@/router'

// Chave usada por versões antigas do front; só é limpa, nunca lida
const ACCESS_TOKEN_KEY = 'access_token'

export const BASE_URL = (
  import.meta.env.VITE_API_URL ||
  import.meta.env.VITE_API_BASE_URL ||
  'http://localhost:8080'
).replace(/\/$/, '')
const baseURL = BASE_URL

export class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

function montarUrl(path, params) {
  const url = new URL(`${BASE_URL}${path}`)
  Object.entries(params ?? {}).forEach(([chave, valor]) => {
    if (valor !== null && valor !== undefined && valor !== '') url.searchParams.set(chave, valor)
  })
  return url.toString()
}

// O backend devolve { detail: "texto" } (HTTPException) ou { detail: [...] } (validação)
function extrairMensagem(corpo, status) {
  if (typeof corpo?.detail === 'string') return corpo.detail
  if (typeof corpo?.mensagem === 'string') return corpo.mensagem
  return `Erro ao falar com o servidor (${status}).`
}

// Token da sessão atual (store de login)
function tokenAtual() {
  try {
    return useAuthStore().token
  } catch {
    // Pinia ainda não está ativo (ex.: fora de um componente)
    return null
  }
}

// Sessão recusada pelo servidor: apaga a sessão local e reavalia a rota atual
function sessaoRecusada(status, tokenEnviado) {
  if (status !== 401 || !tokenEnviado) return
  try {
    const auth = useAuthStore()
    if (auth.token !== tokenEnviado) return
    auth.limparSessaoLocal()
    const atual = router.currentRoute.value
    router.replace({ path: atual.fullPath, force: true }).catch(() => {})
  } catch {
    // sem store/roteador ativos: nada a fazer
  }
}

async function request(path, { method = 'GET', params, body, signal, blob = false } = {}) {
  const token = tokenAtual()
  const ehFormData = typeof FormData !== 'undefined' && body instanceof FormData
  let resposta
  try {
    resposta = await fetch(montarUrl(path, params), {
      method,
      signal,
      headers: {
        // FormData (upload) leva o Content-Type com boundary definido pelo navegador
        ...(body && !ehFormData ? { 'Content-Type': 'application/json' } : {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: body ? (ehFormData ? body : JSON.stringify(body)) : undefined,
    })
  } catch (erro) {
    if (erro.name === 'AbortError') throw erro
    throw new ApiError('Não foi possível conectar ao servidor.', 0)
  }

  if (blob && resposta.ok) return resposta.blob()
  const corpo = await resposta.json().catch(() => null)
  if (!resposta.ok) {
    sessaoRecusada(resposta.status, token)
    throw new ApiError(extrairMensagem(corpo, resposta.status), resposta.status)
  }
  return corpo
}

export const api = {
  get: (path, params, options) => request(path, { ...options, params }),
  post: (path, body, options) => request(path, { ...options, method: 'POST', body }),
  put: (path, body, options) => request(path, { ...options, method: 'PUT', body }),
  patch: (path, body, options) => request(path, { ...options, method: 'PATCH', body }),
  delete: (path, options) => request(path, { ...options, method: 'DELETE' }),
}

function url(path) {
  return new URL(path, baseURL).toString()
}

/** @deprecated O token vem da store de login; mantido só para não quebrar imports antigos. */
export function setAccessToken() {}

/** @deprecated Use useAuthStore().logout(). Apenas remove a chave antiga do sessionStorage. */
export function clearAccessToken() {
  try {
    sessionStorage.removeItem(ACCESS_TOKEN_KEY)
  } catch {
    // ignora
  }
}

async function get(path, { params = {} } = {}) {
  const requestUrl = new URL(path, baseURL)

  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null) {
      requestUrl.searchParams.set(key, value)
    }
  }

  const token = tokenAtual()
  const response = await fetch(requestUrl, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  })

  const responseText = await response.text()
  let body = null
  if (responseText) {
    try {
      body = JSON.parse(responseText)
    } catch {
      if (response.ok) {
        throw new Error('A API retornou uma resposta inválida.')
      }
    }
  }

  if (!response.ok) {
    sessaoRecusada(response.status, token)
    const message = body?.detail ?? body?.mensagem
    throw new ApiError(
      typeof message === 'string'
        ? message
        : `Falha na requisição à API: ${response.status} ${response.statusText}`,
      response.status,
    )
  }

  return { data: body }
}

// Versões legadas (devolvem { data }) dos métodos de escrita
const comData = (promessa) => promessa.then((data) => ({ data }))

export default {
  get,
  post: (path, body) => comData(request(path, { method: 'POST', body })),
  put: (path, body) => comData(request(path, { method: 'PUT', body })),
  patch: (path, body) => comData(request(path, { method: 'PATCH', body })),
  delete: (path) => comData(request(path, { method: 'DELETE' })),
  url,
  setAccessToken,
  clearAccessToken,
}
