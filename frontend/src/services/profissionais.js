/**
 * profissionais — chamadas da API relacionadas a especialidades e busca de profissionais
 *
 * COMO USAR:
 *
 *   import { listarEspecialidades, buscarProfissionais, maisAvaliados } from '@/services/profissionais'
 *
 *   const especialidades = await listarEspecialidades()
 *   // [{ id_especialidade: 1, especialidade: 'Cardiologia' }, ...]
 *
 *   const resultado = await buscarProfissionais({ id_especialidade: 1, ordenar_por: 'valor' })
 *
 *   const { destaques, total } = await maisAvaliados(4)
 *   // destaques: até 4 profissionais distintos, da maior nota para a menor
 *   // total: quantos profissionais distintos a busca encontrou
 *
 *   // Perfil do profissional e avaliações (PerfilProfissionalLayout / AvaliacoesProfissionalLayout)
 *   const info = await buscarInfoProfissional(id)            // id_profissional (int) ou id_usuario (UUID)
 *   const foto = obterUrlImagemProfissional(info.id_usuario) // URL para <img>
 *   const res = await buscarAvaliacoesProfissional({ id_usuario: info.id_usuario })
 *   const { nota, total, distribuicao } = calcularResumoAvaliacoes(res.total, res.sub_total)
 *
 * ENDPOINTS USADOS
 *   GET  /profissionais/lista-especialidade                 lista pública de especialidades
 *   GET  /api/v1/profissionais/busca                        busca pública (só traz quem tem horário livre)
 *   GET  /profissionais/buscar-info-profissional/{id}       dados cadastrais e especialidades
 *   GET  /profissionais/buscar-imagem-profissional/{id}     foto do profissional (404 se não houver)
 *   POST /avaliacao/buscar-avaliacoes                       avaliações e contagem por nota
 */

import { api, BASE_URL } from '@/services/api'

export function listarEspecialidades(options) {
  return api.get('/profissionais/lista-especialidade', null, options)
}

/**
 * Filtros aceitos (todos opcionais): id_especialidade, especialidade, data_inicio, data_fim,
 * hora_inicio, hora_fim, valor_min, valor_max, ordenar_por ('nome' | 'valor' | 'avaliacao').
 */
export function buscarProfissionais(filtros = {}, options) {
  return api.get('/api/v1/profissionais/busca', filtros, options)
}

/**
 * Os `limite` profissionais mais bem avaliados.
 * A busca devolve um item por vínculo profissional+especialidade; aqui o mesmo
 * profissional aparece uma vez só, com a especialidade de maior nota.
 * Quem ainda não foi avaliado só entra se faltar gente avaliada.
 */
export async function maisAvaliados(limite = 4, options) {
  const lista = await buscarProfissionais({ ordenar_por: 'avaliacao' }, options)

  const vistos = new Set()
  const unicos = []
  for (const item of lista) {
    if (vistos.has(item.id_profissional)) continue
    vistos.add(item.id_profissional)
    unicos.push(item)
  }
  return { destaques: unicos.slice(0, limite), total: unicos.length }
}

/* ------------------------------------------------------------------ */
/* Perfil do profissional e avaliações                                 */
/* ------------------------------------------------------------------ */

/**
 * Dados cadastrais e especialidades de um profissional.
 * `id` aceita o id_profissional (inteiro) ou o id_usuario (UUID).
 */
export function buscarInfoProfissional(id, options) {
  return api.get(`/profissionais/buscar-info-profissional/${id}`, null, options)
}

/**
 * URL completa da foto, pronta para usar em <img :src>.
 * O backend responde 404 quando o profissional não tem foto.
 */
export function obterUrlImagemProfissional(id) {
  if (!id) return ''
  return `${BASE_URL}/profissionais/buscar-imagem-profissional/${id}`
}

/**
 * Avaliações do profissional e contagem por nota.
 * dados: { id_usuario, id_especialidade? } — sem id_especialidade, traz todas.
 * Se retornar 400 ou 404 (ex.: sem avaliações cadastradas), devolve objeto vazio
 * com total=0 em vez de lançar exceção.
 */
export async function buscarAvaliacoesProfissional(dados, options) {
  if (!dados?.id_usuario) {
    return {
      avaliacao: [],
      total: 0,
      sub_total: { '1': 0, '2': 0, '3': 0, '4': 0, '5': 0 },
    }
  }

  try {
    return await api.post('/avaliacao/buscar-avaliacoes', dados, options)
  } catch (erro) {
    if (erro.status === 400 || erro.status === 404) {
      return {
        avaliacao: [],
        total: 0,
        sub_total: { '1': 0, '2': 0, '3': 0, '4': 0, '5': 0 },
      }
    }
    throw erro
  }
}

/**
 * Transforma `total` e `sub_total` ({ '1': n, ..., '5': n }) na nota média (só das
 * avaliações com estrelas)
 * e no array de distribuição (de 5 a 1 estrelas) usado pelo ResumoAvaliacoes.
 */
export function calcularResumoAvaliacoes(total = 0, subTotal = {}) {
  const distribuicao = [
    { stars: 5, count: subTotal?.['5'] ?? 0 },
    { stars: 4, count: subTotal?.['4'] ?? 0 },
    { stars: 3, count: subTotal?.['3'] ?? 0 },
    { stars: 2, count: subTotal?.['2'] ?? 0 },
    { stars: 1, count: subTotal?.['1'] ?? 0 },
  ]
  // A média considera só quem deu estrelas; `total` inclui avaliações só com comentário
  let soma = 0
  let comNota = 0
  for (let i = 1; i <= 5; i++) {
    const quantidade = subTotal?.[String(i)] ?? 0
    soma += i * quantidade
    comNota += quantidade
  }
  const nota = comNota > 0 ? Number((soma / comNota).toFixed(1)) : 0
  return { nota, total, distribuicao }
}
