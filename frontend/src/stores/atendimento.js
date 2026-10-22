import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

/**
 * Estado do atendimento em andamento, compartilhado entre as telas
 * de chamada, receita e atestado do profissional.
 *
 * TODO: trocar os dados de exemplo pelos dados da consulta vindos da API.
 */
export const useAtendimentoStore = defineStore('atendimento', () => {
  const paciente = ref({
    nome: 'Fulano',
    idade: 34,
    cpf: '321.***.***-00',
  })

  // Início da teleconsulta (usado no cronômetro e no texto do atestado)
  const inicio = ref(new Date())

  // Retorno clínico: 'nao' | 30 | 60 | 'personalizado'
  const retorno = ref(30)
  const retornoData = ref('')

  // ---------- Receita ----------
  const medicamentos = ref([
    {
      id: 1,
      nome: 'Sertralina 100mg - Comprimido',
      posologia: 'Tomar 1 comprimido via oral 1 vez ao dia.',
      quantidade: '2 caixas (60 comp).',
    },
  ])
  const recomendacoes = ref('Praticar atividade física diariamente.')
  const validadeReceita = ref(60)

  let proximoId = 2
  function adicionarMedicamento(nome = '') {
    const medicamento = { id: proximoId++, nome, posologia: '', quantidade: '' }
    medicamentos.value.push(medicamento)
    return medicamento
  }

  function removerMedicamento(id) {
    medicamentos.value = medicamentos.value.filter((m) => m.id !== id)
  }

  // ---------- Atestado ----------
  const diasAfastamento = ref(2)
  const atestadoTexto = ref(null) // null = usa o texto gerado automaticamente

  const atestadoGerado = computed(() => {
    const fmtHora = (d) =>
      `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
    const data = inicio.value
    const fim = new Date(data.getTime() + 35 * 60 * 1000)
    const retornoTrabalho = new Date(data)
    retornoTrabalho.setDate(retornoTrabalho.getDate() + diasAfastamento.value)

    const dataExtenso = data.toLocaleDateString('pt-BR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    })
    const extenso = ['zero', 'um', 'dois', 'três', 'quatro', 'cinco', 'seis', 'sete', 'oito', 'nove', 'dez']
    const dias = diasAfastamento.value
    const diasTexto = `${dias} (${extenso[dias] ?? dias}) ${dias === 1 ? 'dia' : 'dias'}`

    return (
      `Atesto, para os devidos fins de comprovação, que a Sr. ${paciente.value.nome}, ` +
      `portador do CPF nº ${paciente.value.cpf}, esteve sob meus cuidados profissionais em ` +
      `teleconsulta médica realizada nesta data, ${dataExtenso}, no horário das ` +
      `${fmtHora(data)} às ${fmtHora(fim)}.\n\n` +
      `Em virtude de quadro clínico avaliado, a paciente necessita de ${diasTexto} de repouso ` +
      `domiciliar e afastamento de suas atividades laborais e correlatas a contar desta data, ` +
      `devendo retornar às suas funções em ${retornoTrabalho.toLocaleDateString('pt-BR')}.`
    )
  })

  const atestado = computed({
    get: () => atestadoTexto.value ?? atestadoGerado.value,
    set: (texto) => (atestadoTexto.value = texto),
  })

  return {
    paciente,
    inicio,
    retorno,
    retornoData,
    medicamentos,
    recomendacoes,
    validadeReceita,
    adicionarMedicamento,
    removerMedicamento,
    diasAfastamento,
    atestado,
  }
})
