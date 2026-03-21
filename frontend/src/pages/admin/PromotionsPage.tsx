import { useQuery } from '@tanstack/react-query'
import { adminApi } from '../../api/admin'
import { Card } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'
import { Spinner } from '../../components/ui/Spinner'

export function PromotionsPage() {
  const { data: promos, isLoading } = useQuery({
    queryKey: ['admin-promotions'],
    queryFn: adminApi.getPromotions,
  })

  if (isLoading) return <Spinner className="py-20" />

  return (
    <div className="flex flex-col gap-4 pb-6 px-4">
      <h1 className="text-xl font-bold pt-4">Акции и промо</h1>

      {promos?.map((p: any) => (
        <Card key={p.id}>
          <div className="flex justify-between items-start mb-2">
            <h3 className="font-semibold">{p.title}</h3>
            <Badge className={p.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}>
              {p.is_active ? 'Активна' : 'Архив'}
            </Badge>
          </div>
          {p.description && <p className="text-sm text-[var(--hint-color)]">{p.description}</p>}
          <div className="text-xs text-[var(--hint-color)] mt-2">
            {p.date_start} — {p.date_end}
          </div>
        </Card>
      ))}
    </div>
  )
}
