/**
 * Formas e estados do pagamento (os mesmos valores da API /api/v1/pagamento).
 */

export const METODOS_PAGAMENTO = [
  { id: 'pix', nome: 'Pix', descricao: 'Pagamento instantâneo com QR Code', simbolo: '▣' },
  { id: 'cartao', nome: 'Cartão de Crédito ou Débito', descricao: 'Parcele em até 10x no crédito', simbolo: '▰' },
  { id: 'boleto', nome: 'Boleto Bancário', descricao: 'Compensação em até 3 dias úteis', simbolo: '▥' },
]

export const nomeMetodo = (id) => METODOS_PAGAMENTO.find((m) => m.id === id)?.nome ?? ''

// pendente | aprovado | recusado | cancelado
export const STATUS_PAGAMENTO = {
  aprovado: {
    rotulo: 'Aprovado',
    titulo: 'Pagamento aprovado!',
    mensagem: 'Recebemos o seu pagamento. A consulta está confirmada e o link da chamada fica disponível em Meus Agendamentos.',
    cor: 'text-[#08805f]',
    fundo: 'bg-[#e3f7ef]',
    icone: 'M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z',
  },
  pendente: {
    rotulo: 'Pendente',
    titulo: 'Pagamento pendente',
    mensagem: 'O pagamento ainda não foi confirmado. Pix e boleto podem levar alguns instantes (o boleto, até 3 dias úteis) para compensar.',
    cor: 'text-[#a96a05]',
    fundo: 'bg-[#fff4de]',
    icone: 'M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z',
  },
  recusado: {
    rotulo: 'Recusado',
    titulo: 'Pagamento recusado',
    mensagem: 'O pagamento não foi aprovado. Nenhum valor foi cobrado. Tente novamente ou escolha outra forma de pagamento.',
    cor: 'text-[#c02a46]',
    fundo: 'bg-[#fdecef]',
    icone: 'm9.75 9.75 4.5 4.5m0-4.5-4.5 4.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z',
  },
  cancelado: {
    rotulo: 'Cancelado',
    titulo: 'Pagamento cancelado',
    mensagem: 'O pagamento foi cancelado ou estornado. Se ainda quiser a consulta, faça um novo pagamento.',
    cor: 'text-[#59636d]',
    fundo: 'bg-[#eef1f4]',
    icone: 'M18.364 18.364A9 9 0 0 0 5.636 5.636m12.728 12.728A9 9 0 0 1 5.636 5.636m12.728 12.728L5.636 5.636',
  },
}

export const infoStatusPagamento = (status) => STATUS_PAGAMENTO[status] ?? null
