import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { adminApi } from '../../api/admin'
import { Card } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'
import { Spinner } from '../../components/ui/Spinner'
import { formatPrice } from '../../utils/format'
import { haptic, hapticSuccess, hapticError } from '../../utils/telegram'

export function ServicesManagePage() {
  const queryClient = useQueryClient()

  const { data: services, isLoading } = useQuery({
    queryKey: ['admin-services'],
    queryFn: adminApi.getServices,
  })

  const { data: categories } = useQuery({
    queryKey: ['admin-categories'],
    queryFn: adminApi.getCategories,
  })

  const toggleMutation = useMutation({
    mutationFn: ({ id, is_active }: { id: number; is_active: boolean }) =>
      adminApi.updateService(id, { is_active }),
    onSuccess: () => {
      hapticSuccess()
      queryClient.invalidateQueries({ queryKey: ['admin-services'] })
    },
    onError: () => {
      hapticError()
    },
  })

  if (isLoading) return <Spinner className="py-20" />

  const catMap = new Map(categories?.map((c: any) => [c.id, c.name]) || [])

  // Group services by category
  const grouped = new Map<number, { name: string; services: any[] }>()
  services?.forEach((s: any) => {
    const catId = s.category_id
    if (!grouped.has(catId)) {
      grouped.set(catId, { name: catMap.get(catId) || 'Без категории', services: [] })
    }
    grouped.get(catId)!.services.push(s)
  })

  return (
    <div className="flex flex-col gap-4 pb-6 px-4">
      <h1 className="text-xl font-bold pt-4">Управление услугами</h1>

      {Array.from(grouped.entries()).map(([catId, group]) => (
        <div key={catId} className="flex flex-col gap-3">
          <h2 className="text-sm font-semibold text-[var(--hint-color)] uppercase tracking-wide mt-2">
            {group.name}
          </h2>

          {group.services.map((s: any) => (
            <Card key={s.id}>
              <div className="flex justify-between items-start mb-2">
                <div className="flex-1 min-w-0 mr-3">
                  <h3 className="font-semibold">{s.name}</h3>
                  {s.description && (
                    <p className="text-xs text-[var(--hint-color)] mt-0.5 line-clamp-2">{s.description}</p>
                  )}
                </div>
                <button
                  onClick={() => {
                    haptic('medium')
                    toggleMutation.mutate({ id: s.id, is_active: !s.is_active })
                  }}
                  disabled={toggleMutation.isPending}
                  className={`relative inline-flex h-7 w-12 shrink-0 cursor-pointer items-center rounded-full transition-colors duration-200 focus:outline-none disabled:opacity-50 ${
                    s.is_active ? 'bg-green-500' : 'bg-gray-300'
                  }`}
                  aria-label={s.is_active ? 'Деактивировать' : 'Активировать'}
                >
                  <span
                    className={`inline-block h-5 w-5 rounded-full bg-white shadow-sm transition-transform duration-200 ${
                      s.is_active ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>

              <div className="text-sm text-[var(--hint-color)] flex flex-col gap-1">
                <div className="flex items-center gap-2">
                  <span>&#9201; {s.duration_min_hours}&mdash;{s.duration_max_hours} ч</span>
                  <Badge className={s.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}>
                    {s.is_active ? 'Активна' : 'Скрыта'}
                  </Badge>
                </div>
                {s.prices && s.prices.length > 0 && (
                  <div className="mt-1 grid grid-cols-1 gap-0.5">
                    {s.prices.map((p: any) => (
                      <div key={p.id} className="flex justify-between text-xs">
                        <span className="text-[var(--hint-color)]">
                          {p.car_class || p.package_name || 'Стандарт'}
                        </span>
                        <span className="font-medium text-[var(--text-color)]">
                          от {formatPrice(p.price_from)}
                          {p.price_to ? ` до ${formatPrice(p.price_to)}` : ''}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>
      ))}

      {(!services || services.length === 0) && (
        <p className="text-center text-[var(--hint-color)] py-10">Услуг пока нет</p>
      )}
    </div>
  )
}
