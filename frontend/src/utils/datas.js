// Helpers de data usados nas telas do paciente.
// Todas as datas circulam como string ISO 'YYYY-MM-DD'.

export const MESES = [
  'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro',
]
export const MESES_ABREV = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
export const DIAS_SEMANA = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']

const pad = (n) => String(n).padStart(2, '0')

// Date -> 'YYYY-MM-DD' no fuso local (sem converter para UTC)
export function toISO(date) {
  if (!date || !(date instanceof Date) || isNaN(date.getTime())) return ''
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
}

// 'YYYY-MM-DD' -> Date local. new Date('2024-05-15') seria UTC e poderia cair no dia anterior.
export function fromISO(iso) {
  if (!iso || typeof iso !== 'string') return new Date()
  const partes = iso.split('-').map(Number)
  if (partes.length < 3 || partes.some(isNaN)) return new Date(iso)
  const [y, m, d] = partes
  return new Date(y, m - 1, d)
}

// '2024-05-21' -> 'Terça, 21 de Maio'
export function diaPorExtenso(iso) {
  if (!iso) return ''
  const dt = fromISO(iso)
  if (isNaN(dt.getTime())) return String(iso)
  return `${DIAS_SEMANA[dt.getDay()]}, ${dt.getDate()} de ${MESES[dt.getMonth()]}`
}

// '2024-05-15' -> '15 Mai 2024'
export function dataCurta(iso) {
  if (!iso) return ''
  const dt = fromISO(iso)
  if (isNaN(dt.getTime())) return String(iso)
  return `${pad(dt.getDate())} ${MESES_ABREV[dt.getMonth()]} ${dt.getFullYear()}`
}

// '2024-05-12' -> '12 de Maio, 2024'
export function dataLonga(iso) {
  if (!iso) return ''
  const dt = fromISO(iso)
  if (isNaN(dt.getTime())) return String(iso)
  return `${pad(dt.getDate())} de ${MESES[dt.getMonth()]}, ${dt.getFullYear()}`
}
