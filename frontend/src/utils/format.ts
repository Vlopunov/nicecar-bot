const MONTHS = [
  '', 'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
  'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря',
]

const MONTHS_SHORT = [
  '', 'янв', 'фев', 'мар', 'апр', 'май', 'июн',
  'июл', 'авг', 'сен', 'окт', 'ноя', 'дек',
]

export function formatPrice(price: number | null | undefined): string {
  if (price == null) return 'по запросу'
  if (Number.isInteger(price)) return `${price} BYN`
  return `${price.toFixed(2)} BYN`
}

export function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return `${d.getDate()} ${MONTHS[d.getMonth() + 1]}`
}

export function formatDateShort(dateStr: string): string {
  const d = new Date(dateStr)
  return `${d.getDate()} ${MONTHS_SHORT[d.getMonth() + 1]}`
}

export function formatDateFull(dateStr: string): string {
  const d = new Date(dateStr)
  const days = ['вс', 'пн', 'вт', 'ср', 'чт', 'пт', 'сб']
  return `${days[d.getDay()]}, ${d.getDate()} ${MONTHS[d.getMonth() + 1]}`
}

export function getStatusLabel(status: string): string {
  const map: Record<string, string> = {
    new: 'Новая',
    confirmed: 'Подтверждена',
    in_progress: 'В работе',
    completed: 'Завершена',
    cancelled: 'Отменена',
    no_show: 'Не явился',
  }
  return map[status] || status
}

export function getStatusColor(status: string): string {
  const map: Record<string, string> = {
    new: 'bg-blue-100 text-blue-700',
    confirmed: 'bg-green-100 text-green-700',
    in_progress: 'bg-yellow-100 text-yellow-700',
    completed: 'bg-gray-100 text-gray-600',
    cancelled: 'bg-red-100 text-red-700',
    no_show: 'bg-orange-100 text-orange-700',
  }
  return map[status] || 'bg-gray-100 text-gray-600'
}
