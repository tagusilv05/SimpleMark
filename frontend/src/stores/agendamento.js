import { ref } from 'vue'
import { defineStore } from 'pinia'
import { api } from '@/services/api'

/**
 * Agendamento em andamento, compartilhado entre as telas
 * Agendamento -> Confirmação do agendamento -> Pagamento.
 *
 *   consulta  resposta de POST /consultas/agendar (mesmo formato de GET /consultas/minhas/{id})
 *   horario   { id_horario, inicio: 'HH:MM', fim: 'HH:MM' } escolhido na tela de agendamento
 */
export const useAgendamentoStore = defineStore('agendamento', () => {
  const consulta = ref(null)
  const horario = ref(null)

  // Cria a consulta no horário escolhido. O backend tira profissional, data, hora e valor do horário.
  async function agendar(horarioEscolhido) {
    consulta.value = await api.post('/consultas/agendar', { id_horario: horarioEscolhido.id_horario })
    horario.value = horarioEscolhido
    return consulta.value
  }

  // Recarrega a consulta pelo id (ex.: confirmação aberta direto pela URL)
  async function carregar(idConsulta) {
    consulta.value = await api.get(`/consultas/minhas/${idConsulta}`)
    if (horario.value?.inicio !== consulta.value.hora.slice(0, 5)) horario.value = null
    return consulta.value
  }

  return { consulta, horario, agendar, carregar }
})
