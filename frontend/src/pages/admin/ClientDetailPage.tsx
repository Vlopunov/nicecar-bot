import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { adminApi } from '../../api/admin'
import { Card } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'
import { Spinner } from '../../components/ui/Spinner'
import { formatDate, getStatusLabel, getStatusColor, formatPrice } from '../../utils/format'

export function ClientDetailPage() {
  const { id } = useParams<{ id: string }>()

  const { data: user, isLoading } = useQuery({
    queryKey: ['admin-user', id],
    queryFn: () => adminApi.getUser(Number(id)),
    enabled: !!id,
  })

  if (isLoading) return <Spinner className="py-20" />
  if (!user) return <p className="p-4">Клиент не найден</p>

  return (
    <div className="flex flex-col gap-4 pb-6 px-4">
      <h1 className="text-xl font-bold pt-4">{user.first_name} {user.last_name || ''}</h1>

      <Card>
        <div className="flex flex-col gap-2 text-sm">
          {user.username && <div><span className="text-[var(--hint-color)]">Telegram:</span> @{user.username}</div>}
          {user.phone && <div><span className="text-[var(--hint-color)]">Телефон:</span> {user.phone}</div>}
          <div><span className="text-[var(--hint-color)]">ID:</span> {user.telegram_id}</div>
          <div><span className="text-[var(--hint-color)]">Регистрация:</span> {user.created_at ? new Date(user.created_at).toLocaleDateString('ru') : ''}</div>
        </div>
      </Card>

      <div className="grid grid-cols-3 gap-3">
        <Card className="text-center">
          <div className="text-xl font-bold">{user.visit_count}</div>
          <div className="text-xs text-[var(--hint-color)]">Визиты</div>
        </Card>
        <Card className="text-center">
          <div className="text-xl font-bold text-accent">{user.bonus_balance.toFixed(0)}</div>
          <div className="text-xs text-[var(--hint-color)]">Бонусы</div>
        </Card>
        <Card className="text-center">
          <div className="text-xl font-bold">{user.total_spent.toFixed(0)}</div>
          <div className="text-xs text-[var(--hint-color)]">Потрачено</div>
        </Card>
      </div>

      {user.tags && (
        <div className="flex gap-2 flex-wrap">
          {user.tags.split(',').map((t: string) => (
            <span key={t} className="bg-accent/10 text-accent text-xs px-3 py-1 rounded-full">{t.trim()}</span>
          ))}
        </div>
      )}

      {user.notes && (
        <Card>
          <h3 className="font-semibold mb-1 text-sm">Заметки</h3>
          <p className="text-sm text-[var(--hint-color)]">{user.notes}</p>
        </Card>
      )}

      <h2 className="font-semibold mt-2">История записей</h2>
      {user.bookings?.map((b: any) => (
        <Card key={b.id}>
          <div className="flex justify-between items-start">
            <div>
              <p className="font-medium">{b.service_name}</p>
              <p className="text-sm text-[var(--hint-color)]">{formatDate(b.date)}</p>
            </div>
            <div className="text-right">
              <Badge className={getStatusColor(b.status)}>{getStatusLabel(b.status)}</Badge>
              {b.price_final && <p className="text-sm mt-1">{formatPrice(b.price_final)}</p>}
            </div>
          </div>
        </Card>
      ))}
    </div>
  )
}
