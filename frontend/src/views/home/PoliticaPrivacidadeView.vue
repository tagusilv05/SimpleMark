<script setup>
/**
 * PoliticaPrivacidadeView — página "Política de Privacidade"
 *
 * Fluxo: home -> rodapé "Política de Privacidade" -> esta tela (rota `privacidade`)
 *        -> Voltar -> home.
 *
 * ⚠️ O texto abaixo é uma PROPOSTA base, alinhada à LGPD (Lei nº 13.709/2018) e aos dados
 * que as telas de cadastro realmente coletam. Antes de publicar, peça a revisão de quem for
 * responsável pelo jurídico/DPO do projeto (prazos de retenção, operadores e parceiros de
 * pagamento, por exemplo, precisam ser confirmados).
 *
 * Edite o array `secoes` para mudar o conteúdo; a numeração e o índice são automáticos.
 */

import DocumentoInstitucional from '@/components/shared/DocumentoInstitucional.vue'

const atualizadoEm = '28 de outubro de 2026'

const secoes = [
  {
    titulo: 'Introdução',
    paragrafos: [
      'A Simple Mark respeita a sua privacidade e trata dados pessoais em conformidade com a Lei Geral de Proteção de Dados (LGPD – Lei nº 13.709/2018). Esta política explica quais dados coletamos, para que os usamos, com quem os compartilhamos e como você pode exercer os seus direitos.',
      'Como a plataforma envolve informações de saúde, que são dados pessoais sensíveis, aplicamos cuidados reforçados no seu tratamento.',
    ],
  },
  {
    titulo: 'Dados que coletamos',
    paragrafos: ['Coletamos os dados necessários para o funcionamento da plataforma:'],
    itens: [
      'Dados de cadastro: nome completo, data de nascimento, gênero, CPF, órgão emissor do documento, e-mail, celular, CEP e endereço.',
      'Dados de profissionais: registro profissional e informações profissionais (como formação e tempo de atuação), usados na validação do perfil.',
      'Dados de saúde: informações compartilhadas durante o atendimento, como relatos, receitas, pedidos de exames e atestados.',
      'Dados de pagamento: informações necessárias para processar o pagamento por Pix ou cartão, tratadas por meio de parceiros de pagamento.',
      'Dados de uso e técnicos: informações de acesso, como data e hora, tipo de navegador e dispositivo, para segurança e melhoria do serviço.',
      'Dados de manifestações: o conteúdo e os anexos enviados à Ouvidoria.',
    ],
  },
  {
    titulo: 'Para que usamos os seus dados',
    itens: [
      'Criar e administrar a sua conta e autenticar o seu acesso.',
      'Permitir a busca de profissionais, o agendamento e a realização das teleconsultas.',
      'Viabilizar a emissão de receitas, pedidos de exames e atestados digitais.',
      'Processar pagamentos e confirmar agendamentos.',
      'Validar o registro e o perfil dos profissionais de saúde.',
      'Enviar lembretes de consulta e comunicações relacionadas ao serviço.',
      'Analisar e responder às manifestações da Ouvidoria.',
      'Garantir a segurança da plataforma, prevenir fraudes e cumprir obrigações legais e regulatórias.',
    ],
  },
  {
    titulo: 'Bases legais',
    paragrafos: [
      'O tratamento de dados pessoais é realizado com base na LGPD, em especial: execução de contrato ou de procedimentos preliminares, cumprimento de obrigação legal ou regulatória, exercício regular de direitos e legítimo interesse.',
      'Os dados pessoais sensíveis, como os de saúde, são tratados com o seu consentimento ou nas demais hipóteses previstas no art. 11 da LGPD, como a tutela da saúde em procedimentos realizados por profissionais de saúde.',
    ],
  },
  {
    titulo: 'Compartilhamento de dados',
    paragrafos: ['Não vendemos os seus dados pessoais. Eles podem ser compartilhados apenas:'],
    itens: [
      'Com o profissional de saúde responsável pelo seu atendimento, na medida necessária para a consulta.',
      'Com parceiros e prestadores de serviço, como processamento de pagamentos e infraestrutura tecnológica, que seguem as nossas instruções e as regras de proteção de dados.',
      'Com autoridades públicas, quando houver obrigação legal ou determinação judicial.',
    ],
  },
  {
    titulo: 'Segurança das informações',
    paragrafos: [
      'Adotamos medidas técnicas e organizacionais para proteger os seus dados contra acessos não autorizados, perda, alteração ou divulgação indevida. As teleconsultas são realizadas em ambiente privativo e criptografado, e o acesso às informações é restrito a quem precisa delas para executar suas atividades.',
      'Nenhum sistema é totalmente imune a riscos. Por isso, mantenha a sua senha em sigilo e não a compartilhe com terceiros.',
    ],
  },
  {
    titulo: 'Por quanto tempo guardamos os dados',
    paragrafos: [
      'Mantemos os dados pelo tempo necessário para cumprir as finalidades descritas nesta política e as obrigações legais e regulatórias aplicáveis, incluindo os prazos de guarda de registros de atendimento de saúde. Depois disso, os dados são eliminados ou anonimizados, salvo quando a lei permitir ou exigir a sua conservação.',
    ],
  },
  {
    titulo: 'Seus direitos como titular',
    paragrafos: ['Nos termos do art. 18 da LGPD, você pode solicitar, a qualquer momento:'],
    itens: [
      'A confirmação de que tratamos os seus dados e o acesso a eles.',
      'A correção de dados incompletos, inexatos ou desatualizados.',
      'A anonimização, o bloqueio ou a eliminação de dados desnecessários ou tratados em desconformidade.',
      'A portabilidade dos dados, observadas as regras aplicáveis.',
      'Informações sobre com quem os dados são compartilhados.',
      'A revogação do consentimento, quando essa for a base legal do tratamento.',
    ],
    fechamento: [
      'Para exercer esses direitos, utilize a página de Ouvidoria da plataforma. Algumas solicitações podem ter limitações legais, como a obrigação de guarda de registros de saúde.',
    ],
  },
  {
    titulo: 'Menores de idade',
    paragrafos: [
      'A plataforma é destinada a maiores de 18 anos. O atendimento de crianças e adolescentes deve ser feito com a participação e a responsabilidade de um representante legal, que fornece e acompanha os dados.',
    ],
  },
  {
    titulo: 'Alterações desta política',
    paragrafos: [
      'Esta política pode ser atualizada para refletir mudanças na plataforma ou na legislação. A data da última atualização é indicada no topo da página. Em caso de mudanças relevantes, avisaremos pelos canais da plataforma.',
    ],
  },
  {
    titulo: 'Contato',
    paragrafos: [
      'Dúvidas, solicitações ou reclamações sobre privacidade e proteção de dados podem ser enviadas pela página de Ouvidoria da plataforma.',
    ],
  },
]
</script>

<template>
  <DocumentoInstitucional
    titulo="Política de Privacidade"
    resumo="Saiba como a Simple Mark coleta, usa, protege e compartilha os seus dados pessoais, e como você pode exercer os seus direitos."
    :atualizado-em="atualizadoEm"
    :secoes="secoes"
  />
</template>