import { haptic } from '../../utils/telegram'

interface Props {
  selected: string | null
  onSelect: (cls: string) => void
}

const CAR_CLASSES = [
  { id: 'I', label: 'I класс', examples: 'Golf, Focus, Solaris' },
  { id: 'II', label: 'II класс', examples: 'RAV4, Tiguan, Mazda 6' },
  { id: 'III', label: 'III класс', examples: 'BMW 7, X-Trail, Audi Q5' },
]

export function CarClassSelector({ selected, onSelect }: Props) {
  return (
    <div className="flex flex-col gap-2">
      {CAR_CLASSES.map(cls => (
        <button
          key={cls.id}
          onClick={() => { haptic(); onSelect(cls.id) }}
          className={`
            p-4 rounded-xl text-left transition border-2
            ${selected === cls.id
              ? 'border-accent bg-accent/5'
              : 'border-transparent bg-[var(--secondary-bg)]'
            }
          `}
        >
          <div className="font-semibold">{cls.label}</div>
          <div className="text-sm text-[var(--hint-color)]">{cls.examples}</div>
        </button>
      ))}
    </div>
  )
}
