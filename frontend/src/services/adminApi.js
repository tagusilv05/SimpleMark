/**
 * adminApi — chamadas das telas de administração.
 *
 * Usa o mesmo cliente HTTP do resto do app (services/api.js), então o token vem
 * da sessão de login (store) e um 401 encerra a sessão local. Devolve { data }.
 */
import api from '@/services/api'

export default {
  get: (path, options) => api.get(path, options),
  post: (path, body) => api.post(path, body),
}
