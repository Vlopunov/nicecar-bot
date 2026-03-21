import { useQuery } from '@tanstack/react-query'
import { adminApi } from '../../api/admin'
import { Card } from '../../components/ui/Card'
import { Spinner } from '../../components/ui/Spinner'

export function PortfolioManagePage() {
  const { data: items, isLoading } = useQuery({
    queryKey: ['admin-portfolio'],
    queryFn: adminApi.getPortfolio,
  })

  if (isLoading) return <Spinner className="py-20" />

  return (
    <div className="flex flex-col gap-4 pb-6 px-4">
      <h1 className="text-xl font-bold pt-4">Управление портфолио</h1>

      <div className="grid grid-cols-2 gap-3">
        {items?.map((item: any) => (
          <Card key={item.id} className="p-2">
            <div className="aspect-square rounded-xl overflow-hidden mb-2">
              <img src={item.image_url} alt="" className="w-full h-full object-cover" loading="lazy" />
            </div>
            <p className="text-xs font-medium">{item.car_brand} {item.car_model}</p>
            <p className="text-xs text-[var(--hint-color)]">
              {item.is_visible ? '👁 Видимо' : '🚫 Скрыто'}
            </p>
          </Card>
        ))}
      </div>

      {(!items || items.length === 0) && (
        <p className="text-center text-[var(--hint-color)] py-10">Портфолио пусто</p>
      )}
    </div>
  )
}
