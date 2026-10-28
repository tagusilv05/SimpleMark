<script setup>
/**
 * TermosCondicoesView — página "Termos e Condições"
 *
 * Fluxo: home -> rodapé "Termos e Condições" -> esta tela (rota `termos`) -> Voltar -> home.
 *
 * ⚠️ O texto abaixo é uma PROPOSTA base. Antes de publicar, peça a revisão de quem for
 * responsável pelo jurídico do projeto (valores, prazos, foro e políticas de cancelamento
 * e reembolso, por exemplo, não foram definidos aqui).
 *
 * Edite o array `secoes` para mudar o conteúdo; a numeração e o índice são automáticos.
 */

import DocumentoInstitucional from '@/components/shared/DocumentoInstitucional.vue'

const atualizadoEm = '28 de outubro de 2026'

const secoes = [
  {
    titulo: 'Aceitação dos termos',
    paragrafos: [
      'Ao criar uma conta ou utilizar a plataforma Simple Mark, você declara que leu, compreendeu e concorda com estes Termos e Condições e com a Política de Privacidade.',
      'Se você não concordar com qualquer parte deste documento, não utilize a plataforma.',
    ],
  },
  {
    titulo: 'O que é a Simple Mark',
    paragrafos: [
      'A Simple Mark é uma plataforma digital que aproxima pacientes e profissionais de saúde. Ela permite buscar profissionais, agendar consultas, realizar teleconsultas por vídeo no navegador e receber receitas, pedidos de exames e atestados digitais.',
      'A Simple Mark atua como intermediadora tecnológica. O atendimento clínico é de responsabilidade exclusiva do profissional de saúde que realiza a consulta.',
    ],
  },
  {
    titulo: 'Cadastro e conta',
    itens: [
      'Para usar a plataforma é necessário criar uma conta com dados verdadeiros, completos e atualizados.',
      'O cadastro é destinado a pessoas maiores de 18 anos. Menores de idade devem ser representados por responsável legal.',
      'Você é responsável por manter a confidencialidade da sua senha e por toda atividade realizada na sua conta.',
      'Em caso de suspeita de uso indevido, altere a senha imediatamente e comunique a Ouvidoria.',
    ],
  },
  {
    titulo: 'Uso da teleconsulta',
    paragrafos: [
      'A teleconsulta é realizada pelo navegador, por meio de um link seguro da sala virtual, sem necessidade de instalar aplicativos.',
    ],
    itens: [
      'Mantenha uma conexão de internet estável e um ambiente reservado durante o atendimento.',
      'A gravação ou a divulgação do atendimento por terceiros não é permitida sem autorização expressa de todos os envolvidos.',
      'A teleconsulta tem limitações próprias e pode não ser adequada a todos os casos. O profissional poderá orientar o atendimento presencial quando entender necessário.',
    ],
    fechamento: [
      'A plataforma não substitui o atendimento de urgência ou emergência. Em situações de risco, procure imediatamente um serviço de pronto atendimento ou ligue para o SAMU (192).',
    ],
  },
  {
    titulo: 'Profissionais de saúde',
    itens: [
      'Os profissionais devem informar dados verdadeiros, incluindo o registro profissional, que passam por validação da equipe da Simple Mark antes da liberação do perfil.',
      'Cada profissional responde, ética e legalmente, pelos atendimentos que realiza, pelas orientações prestadas e pelos documentos que emite, em conformidade com a legislação e com as normas do seu conselho profissional.',
      'O profissional é responsável por manter sua agenda atualizada e por registrar e conduzir os atendimentos com sigilo e zelo.',
    ],
  },
  {
    titulo: 'Agendamento e pagamento',
    paragrafos: [
      'Os pacientes visualizam os horários disponíveis na agenda do profissional e escolhem o dia e o horário desejados. A consulta é confirmada após a confirmação do pagamento.',
      'O pagamento pode ser feito por Pix ou cartão de crédito. Os valores e as condições são apresentados antes da confirmação do agendamento.',
      'As regras de cancelamento, remarcação e reembolso são apresentadas na plataforma no momento do agendamento.',
    ],
  },
  {
    titulo: 'Receitas, pedidos de exames e atestados',
    paragrafos: [
      'Receitas, pedidos de exames e atestados digitais são emitidos pelo profissional, a seu critério técnico, ao final do atendimento, e ficam disponíveis ao paciente na plataforma.',
      'A emissão de qualquer documento depende da avaliação do profissional. A Simple Mark não garante a emissão de documentos específicos.',
    ],
  },
  {
    titulo: 'Condutas não permitidas',
    paragrafos: ['Ao usar a plataforma, você se compromete a não:'],
    itens: [
      'Fornecer informações falsas ou usar dados de terceiros sem autorização.',
      'Praticar assédio, discriminação, ofensas ou qualquer forma de violência contra outros usuários.',
      'Tentar acessar áreas restritas, burlar mecanismos de segurança ou comprometer o funcionamento do sistema.',
      'Utilizar a plataforma para fins ilícitos ou contrários à ética profissional e à legislação.',
    ],
    fechamento: [
      'O descumprimento destas regras pode resultar na suspensão ou no encerramento da conta, sem prejuízo das medidas legais cabíveis.',
    ],
  },
  {
    titulo: 'Propriedade intelectual',
    paragrafos: [
      'A marca Simple Mark, o logotipo, o layout, os textos e o código da plataforma são protegidos pela legislação de propriedade intelectual. Não é permitido copiar, modificar ou distribuir esses conteúdos sem autorização.',
    ],
  },
  {
    titulo: 'Limitação de responsabilidade',
    paragrafos: [
      'A Simple Mark emprega esforços razoáveis para manter a plataforma disponível e segura, mas não garante funcionamento ininterrupto. Interrupções podem ocorrer por manutenção, falhas de conexão ou motivos de força maior.',
      'A Simple Mark não se responsabiliza por condutas clínicas, diagnósticos ou prescrições dos profissionais, nem por falhas decorrentes de equipamentos ou da conexão de internet do usuário.',
    ],
  },
  {
    titulo: 'Ouvidoria',
    paragrafos: [
      'Reclamações, sugestões, elogios e dúvidas podem ser registrados a qualquer momento pela página de Ouvidoria da plataforma.',
    ],
  },
  {
    titulo: 'Alterações e legislação aplicável',
    paragrafos: [
      'Estes Termos podem ser atualizados periodicamente. A data da última atualização é indicada no topo desta página, e o uso continuado da plataforma após a alteração representa a concordância com a nova versão.',
      'Estes Termos são regidos pela legislação brasileira.',
    ],
  },
]
</script>

<template>
  <DocumentoInstitucional
    titulo="Termos e Condições"
    resumo="Conheça as regras de uso da plataforma Simple Mark, os direitos e as responsabilidades de pacientes e profissionais de saúde."
    :atualizado-em="atualizadoEm"
    :secoes="secoes"
  />
</template>