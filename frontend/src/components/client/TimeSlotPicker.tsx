import { haptic } from '../../utils/telegram'

interface Props {
  slots: string[]
  selected: string
  onSelect: (time: string) => void
  loading?: boolean
}

export function TimeSlotPicker({ slots, selected, onSelect, loading }: Props) {
  if (loading) {
    return (
      <div className="grid grid-cols-4 gap-2">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="skeleton h-10 rounded-xl" />
        ))}
      </div>
    )
  }

  if (slots.length === 0) {
    return (
      <p className="text-center text-[var(--hint-color)] py-4">
        Нет доступных слотов на эту дату
      </p>
    )
  }

  return (
    <div className="grid grid-cols-4 gap-2">
      {slots.map(slot => (
        <button
          key={slot}
          onClick={() => { haptic(); onSelect(slot) }}
          className={`
            py-2.5 rounded-xl text-sm font-medium transition
            ${selected === slot
              ? 'bg-accent text-white'
              : 'bg-[var(--secondary-bg)] hover:bg-accent/10'
            }
          `}
        >
          {slot}
        </button>
      ))}
    </div>
  )
}
