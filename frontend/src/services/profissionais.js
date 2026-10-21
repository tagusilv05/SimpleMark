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
 * ENDPOINTS USADOS
 *   GET /profissionais/lista-especialidade   lista pública de especialidades
 *   GET /api/v1/profissionais/busca          busca pública (só traz quem tem horário livre)
 */

import { api } from '@/services/api'

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
