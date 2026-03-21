import { useQuery } from '@tanstack/react-query'
import { api } from '../../api/client'
import { PortfolioGallery } from '../../components/client/PortfolioGallery'
import { Spinner } from '../../components/ui/Spinner'
import type { PortfolioItem } from '../../types'

export function PortfolioPage() {
  const { data: items, isLoading } = useQuery({
    queryKey: ['portfolio'],
    queryFn: () => api.get<PortfolioItem[]>('/api/portfolio'),
  })

  if (isLoading) return <Spinner className="py-20" />

  return (
    <div className="flex flex-col gap-4 pb-6 px-4">
      <h1 className="text-xl font-bold pt-4">Наши работы</h1>
      {items && items.length > 0 ? (
        <PortfolioGallery items={items} />
      ) : (
        <p className="text-center text-[var(--hint-color)] py-10">Портфолио скоро будет заполнено</p>
      )}
    </div>
  )
}
