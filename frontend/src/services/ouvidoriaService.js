/**
 * ouvidoriaService — chamadas HTTP da Ouvidoria
 *
 *   POST /api/v1/ouvidoria/manifestacoes  (multipart/form-data)
 *     campos: solicitante, tipo, assunto, descricao, aceite_lgpd, codigo_consulta (opcional)
 *     arquivos: anexos (até 5, PDF/PNG/JPEG, 10 MB cada)
 *     -> 201 { mensagem, id, protocolo, status, criada_em, quantidade_anexos }
 *
 * Não exige login. Se for passado o `token` da conta logada (store de auth), ele vai
 * no cabeçalho e a manifestação fica vinculada à conta.
 *
 * Erros viram `ApiError` com `message` em português, pronta para exibir.
 */
import { ApiError } from '@/services/authService'

const BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8080').replace(/\/$/, '')

/**
 * Abre uma manifestação.
 * @param {{ solicitante: string, tipo: string, assunto: string, descricao: string,
 *           aceiteLgpd: boolean, codigoConsulta?: string, anexos?: File[] }} dados
 * @param {string|null} [token] token Bearer da conta logada (opcional)
 */
export async function abrirManifestacao({
  solicitante,
  tipo,
  assunto,
  descricao,
  aceiteLgpd,
  codigoConsulta,
  anexos = [],
}, token = null) {
  const corpo = new FormData()
  corpo.append('solicitante', solicitante)
  corpo.append('tipo', tipo)
  corpo.append('assunto', assunto)
  corpo.append('descricao', descricao)
  corpo.append('aceite_lgpd', aceiteLgpd ? 'true' : 'false')
  if (codigoConsulta) corpo.append('codigo_consulta', codigoConsulta)
  anexos.forEach((arquivo) => corpo.append('anexos', arquivo))

  let resposta
  try {
    // Sem Content-Type manual: o navegador monta o boundary do multipart
    resposta = await fetch(`${BASE_URL}/api/v1/ouvidoria/manifestacoes`, {
      method: 'POST',
      headers: { Accept: 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
      body: corpo,
    })
  } catch {
    throw new ApiError('Não foi possível conectar ao servidor. Verifique sua conexão e tente novamente.')
  }

  const dados = await resposta.json().catch(() => null)
  if (!resposta.ok) {
    const mensagem =
      (typeof dados?.mensagem === 'string' && dados.mensagem) ||
      (typeof dados?.detail === 'string' && dados.detail) ||
      'Não foi possível enviar a manifestação. Tente novamente.'
    throw new ApiError(mensagem, resposta.status)
  }
  return dados
}
