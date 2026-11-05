import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { api } from '@/services/api'

/**
 * Estado do atendimento em andamento, compartilhado entre as telas
 * de chamada, receita e atestado do profissional.
 *
 * As três telas recebem ?consulta=<id> na URL e chamam carregarConsulta(id), que lê
 * GET /api/v1/consultas/{id}/videochamada:
 *   paciente { nome, idade, cpf }  — cpf já chega mascarado (123.***.***-01)
 *   meet_link                       — sala do Jitsi (usada pela tela de chamada)
 *
 * A receita e o atestado são emitidos em POST /api/v1/receitas e /api/v1/atestados.
 */
export const useAtendimentoStore = defineStore('atendimento', () => {
  const idConsulta = ref(null)
  const paciente = ref({ nome: '', idade: null, cpf: null })

  function definirPaciente(dados) {
    paciente.value = { nome: dados?.nome ?? '', idade: dados?.idade ?? null, cpf: dados?.cpf ?? null }
  }

  // Abre o atendimento de uma consulta. Trocar de consulta limpa o que foi preenchido.
  async function carregarConsulta(id) {
    if (!id) return null
    if (String(idConsulta.value) !== String(id)) {
      idConsulta.value = Number(id)
      definirPaciente(null)
      limparDocumentos()
    }
    const dados = await api.get(`/api/v1/consultas/${id}/videochamada`)
    definirPaciente(dados.paciente)
    return dados
  }

  // Início da teleconsulta (usado no cronômetro e no texto do atestado)
  const inicio = ref(new Date())

  // Retorno clínico: 'nao' | 30 | 60 | 'personalizado'
  const retorno = ref(30)
  const retornoData = ref('')

  // ---------- Receita ----------
  // Cada item: { id, nome, dosagem, posologia, quantidade }
  const medicamentos = ref([])
  const recomendacoes = ref('')
  const validadeReceita = ref(60)
  const receitaEmitida = ref(null) // resposta de POST /receitas

  let proximoId = 1
  function adicionarMedicamento(nome = '') {
    // "Sertralina 100mg" já preenche a dosagem com "100mg"
    const dosagem = nome.match(/\d+(?:[.,]\d+)?\s*(?:mg|mcg|g|ml|ui|%)(?:\/\s*\w+)?/i)?.[0] ?? ''
    const medicamento = { id: proximoId++, nome, dosagem, posologia: '', quantidade: '' }
    medicamentos.value.push(medicamento)
    return medicamento
  }

  function removerMedicamento(id) {
    medicamentos.value = medicamentos.value.filter((m) => m.id !== id)
  }

  async function emitirReceita() {
    receitaEmitida.value = await api.post('/api/v1/receitas', {
      id_consulta: idConsulta.value,
      medicamentos: medicamentos.value.map((m) => ({
        medicamento: m.nome,
        dosagem: m.dosagem,
        posologia: m.posologia,
        quantidade: m.quantidade,
      })),
      validade_dias: validadeReceita.value,
      observacoes: recomendacoes.value.trim() || null,
    })
    return receitaEmitida.value
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
      `Atesto, para os devidos fins de comprovação, que a Sr. ${paciente.value.nome || '__________'}, ` +
      `portador do CPF nº ${paciente.value.cpf || '__________'}, esteve sob meus cuidados profissionais em ` +
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

  const atestadoEmitido = ref(null) // resposta de POST /atestados

  // O texto do atestado vai em observacoes; o afastamento conta a partir de hoje
  async function emitirAtestado() {
    const hoje = new Date()
    const dataInicio = `${hoje.getFullYear()}-${String(hoje.getMonth() + 1).padStart(2, '0')}-${String(hoje.getDate()).padStart(2, '0')}`
    atestadoEmitido.value = await api.post('/api/v1/atestados', {
      id_consulta: idConsulta.value,
      dias_afastamento: diasAfastamento.value,
      data_inicio: dataInicio,
      observacoes: atestado.value.trim(),
    })
    return atestadoEmitido.value
  }

  function limparDocumentos() {
    medicamentos.value = []
    recomendacoes.value = ''
    validadeReceita.value = 60
    receitaEmitida.value = null
    diasAfastamento.value = 2
    atestadoTexto.value = null
    atestadoEmitido.value = null
    inicio.value = new Date()
  }

  return {
    idConsulta,
    carregarConsulta,
    paciente,
    definirPaciente,
    inicio,
    retorno,
    retornoData,
    medicamentos,
    recomendacoes,
    validadeReceita,
    adicionarMedicamento,
    removerMedicamento,
    receitaEmitida,
    emitirReceita,
    diasAfastamento,
    atestado,
    atestadoEmitido,
    emitirAtestado,
  }
})
