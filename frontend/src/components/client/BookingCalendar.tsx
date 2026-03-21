import { useState, useMemo } from 'react'
import { haptic } from '../../utils/telegram'

interface Props {
  selectedDate: string
  onSelect: (date: string) => void
}

const DAYS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
const MONTHS = [
  'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
  'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь',
]

export function BookingCalendar({ selectedDate, onSelect }: Props) {
  const today = new Date()
  const [viewMonth, setViewMonth] = useState(today.getMonth())
  const [viewYear, setViewYear] = useState(today.getFullYear())

  const days = useMemo(() => {
    const firstDay = new Date(viewYear, viewMonth, 1)
    const lastDay = new Date(viewYear, viewMonth + 1, 0)
    const startOffset = (firstDay.getDay() + 6) % 7 // Monday-based

    const result: (Date | null)[] = []
    for (let i = 0; i < startOffset; i++) result.push(null)
    for (let d = 1; d <= lastDay.getDate(); d++) {
      result.push(new Date(viewYear, viewMonth, d))
    }
    return result
  }, [viewMonth, viewYear])

  const isAvailable = (d: Date) => {
    if (d.getDay() === 0) return false // Sunday
    const tomorrow = new Date(today)
    tomorrow.setDate(tomorrow.getDate() + 1)
    tomorrow.setHours(0, 0, 0, 0)
    return d >= tomorrow
  }

  const toStr = (d: Date) => d.toISOString().split('T')[0]

  const prevMonth = () => {
    if (viewMonth === 0) { setViewMonth(11); setViewYear(y => y - 1) }
    else setViewMonth(m => m - 1)
  }

  const nextMonth = () => {
    if (viewMonth === 11) { setViewMonth(0); setViewYear(y => y + 1) }
    else setViewMonth(m => m + 1)
  }

  const canPrev = viewYear > today.getFullYear() || viewMonth > today.getMonth()

  return (
    <div className="bg-[var(--secondary-bg)] rounded-2xl p-4">
      <div className="flex items-center justify-between mb-4">
        <button onClick={prevMonth} disabled={!canPrev}
          className="p-2 rounded-lg hover:bg-[var(--bg-color)] disabled:opacity-30">
          ◀
        </button>
        <span className="font-semibold">{MONTHS[viewMonth]} {viewYear}</span>
        <button onClick={nextMonth}
          className="p-2 rounded-lg hover:bg-[var(--bg-color)]">
          ▶
        </button>
      </div>

      <div className="grid grid-cols-7 gap-1 mb-2">
        {DAYS.map(d => (
          <div key={d} className="text-center text-xs text-[var(--hint-color)] font-medium py-1">{d}</div>
        ))}
      </div>

      <div className="grid grid-cols-7 gap-1">
        {days.map((d, i) => {
          if (!d) return <div key={`empty-${i}`} />
          const available = isAvailable(d)
          const selected = selectedDate === toStr(d)
          const isToday = toStr(d) === toStr(today)

          return (
            <button
              key={toStr(d)}
              disabled={!available}
              onClick={() => { haptic(); onSelect(toStr(d)) }}
              className={`
                aspect-square flex items-center justify-center rounded-xl text-sm font-medium transition
                ${!available ? 'text-[var(--hint-color)] opacity-30 cursor-not-allowed' : 'hover:bg-accent/10 cursor-pointer'}
                ${selected ? 'bg-accent text-white' : ''}
                ${isToday && !selected ? 'ring-2 ring-accent/30' : ''}
              `}
            >
              {d.getDate()}
            </button>
          )
        })}
      </div>
    </div>
  )
}
