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
 * ERROS
 *   Respostas fora de 2xx lançam um ApiError com `status` e `message`.
 *   `message` já vem em português quando o backend envia `detail`.
 *
 * PARÂMETROS (2º argumento do get)
 *   Objeto simples. Valores null / undefined / '' são ignorados.
 */

const BASE_URL = (import.meta.env.VITE_API_URL ?? 'http://localhost:8080').replace(/\/$/, '')

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

async function request(path, { method = 'GET', params, body, signal } = {}) {
  let resposta
  try {
    resposta = await fetch(montarUrl(path, params), {
      method,
      signal,
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    })
  } catch (erro) {
    if (erro.name === 'AbortError') throw erro
    throw new ApiError('Não foi possível conectar ao servidor.', 0)
  }

  const corpo = await resposta.json().catch(() => null)
  if (!resposta.ok) throw new ApiError(extrairMensagem(corpo, resposta.status), resposta.status)
  return corpo
}

export const api = {
  get: (path, params, options) => request(path, { ...options, params }),
  post: (path, body, options) => request(path, { ...options, method: 'POST', body }),
}
