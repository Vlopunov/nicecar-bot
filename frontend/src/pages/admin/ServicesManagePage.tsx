import { useQuery } from '@tanstack/react-query'
import { adminApi } from '../../api/admin'
import { Card } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'
import { Spinner } from '../../components/ui/Spinner'
import { formatPrice } from '../../utils/format'

export function ServicesManagePage() {
  const { data: services, isLoading } = useQuery({
    queryKey: ['admin-services'],
    queryFn: adminApi.getServices,
  })

  const { data: categories } = useQuery({
    queryKey: ['admin-categories'],
    queryFn: adminApi.getCategories,
  })

  if (isLoading) return <Spinner className="py-20" />

  const catMap = new Map(categories?.map((c: any) => [c.id, c.name]) || [])

  return (
    <div className="flex flex-col gap-4 pb-6 px-4">
      <h1 className="text-xl font-bold pt-4">Управление услугами</h1>

      {services?.map((s: any) => (
        <Card key={s.id}>
          <div className="flex justify-between items-start mb-2">
            <div>
              <h3 className="font-semibold">{s.name}</h3>
              <p className="text-xs text-[var(--hint-color)]">{catMap.get(s.category_id) || ''}</p>
            </div>
            <Badge className={s.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}>
              {s.is_active ? 'Активна' : 'Скрыта'}
            </Badge>
          </div>
          <div className="text-sm text-[var(--hint-color)]">
            <div>⏱ {s.duration_min_hours}—{s.duration_max_hours} ч</div>
            {s.prices.length > 0 && (
              <div className="mt-1">
                {s.prices.map((p: any) => (
                  <div key={p.id} className="flex gap-2">
                    <span>{p.car_class || p.package_name || '—'}:</span>
                    <span className="font-medium">от {formatPrice(p.price_from)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </Card>
      ))}
    </div>
  )
}
