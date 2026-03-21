import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { servicesApi } from '../../api/services'
import { ServiceCard } from '../../components/client/ServiceCard'
import { Spinner } from '../../components/ui/Spinner'
import { Input } from '../../components/ui/Input'
import { haptic } from '../../utils/telegram'
import type { ServiceCategory } from '../../types'

export function ServicesPage() {
  const [search, setSearch] = useState('')
  const [activeCategory, setActiveCategory] = useState<number | null>(null)

  const { data: categories, isLoading } = useQuery({
    queryKey: ['services'],
    queryFn: servicesApi.getAll,
  })

  if (isLoading) return <Spinner className="py-20" />

  const filtered = categories
    ?.filter(c => !activeCategory || c.id === activeCategory)
    .map(c => ({
      ...c,
      services: c.services.filter(s =>
        !search || s.name.toLowerCase().includes(search.toLowerCase())
      ),
    }))
    .filter(c => c.services.length > 0)

  return (
    <div className="flex flex-col gap-4 pb-6 px-4">
      <h1 className="text-xl font-bold pt-4">Услуги и цены</h1>

      <Input
        placeholder="Поиск услуги..."
        value={search}
        onChange={e => setSearch(e.target.value)}
      />

      {/* Category filters */}
      <div className="flex gap-2 overflow-x-auto pb-2 -mx-4 px-4 scrollbar-hide">
        <button
          onClick={() => { haptic(); setActiveCategory(null) }}
          className={`shrink-0 px-3 py-1.5 rounded-full text-sm font-medium transition
            ${!activeCategory ? 'bg-accent text-white' : 'bg-[var(--secondary-bg)]'}`}
        >
          Все
        </button>
        {categories?.map(c => (
          <button
            key={c.id}
            onClick={() => { haptic(); setActiveCategory(c.id === activeCategory ? null : c.id) }}
            className={`shrink-0 px-3 py-1.5 rounded-full text-sm font-medium transition
              ${c.id === activeCategory ? 'bg-accent text-white' : 'bg-[var(--secondary-bg)]'}`}
          >
            {c.icon} {c.name}
          </button>
        ))}
      </div>

      {/* Services list */}
      {filtered?.map(cat => (
        <div key={cat.id}>
          <h2 className="font-semibold text-lg mb-2">{cat.icon} {cat.name}</h2>
          <div className="flex flex-col gap-2">
            {cat.services.map(s => <ServiceCard key={s.id} service={s} />)}
          </div>
        </div>
      ))}

      {filtered?.length === 0 && (
        <p className="text-center text-[var(--hint-color)] py-10">Ничего не найдено</p>
      )}
    </div>
  )
}
