// Helpers de URL usados antes de navegar ou embutir links que vêm da API.

const PROTOCOLOS_PERMITIDOS = new Set(['https:', 'http:'])

/**
 * Devolve a URL só se ela for absoluta e usar http(s); caso contrário, null.
 *
 * Links vindos do servidor (sala do Jitsi, checkout do Mercado Pago, validação
 * de documento) vão parar em <iframe :src>, <a :href> ou window.location. Se um
 * deles chegasse como "javascript:..." ou "data:text/html,...", o navegador
 * executaria o código na origem do SimpleMark (XSS). Este filtro bloqueia isso.
 */
export function urlExternaSegura(valor) {
  if (typeof valor !== 'string' || !valor.trim()) return null
  try {
    const url = new URL(valor.trim())
    return PROTOCOLOS_PERMITIDOS.has(url.protocol) ? url.toString() : null
  } catch {
    return null
  }
}
