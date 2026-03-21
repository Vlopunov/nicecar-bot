import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { bookingApi } from '../../api/booking'
import { Card } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { Spinner } from '../../components/ui/Spinner'
import { formatDate, formatPrice, getStatusLabel, getStatusColor } from '../../utils/format'
import { haptic, hapticSuccess } from '../../utils/telegram'

export function HistoryPage() {
  const [filter, setFilter] = useState<string>('all')
  const queryClient = useQueryClient()

  const { data: bookings, isLoading } = useQuery({
    queryKey: ['my-bookings'],
    queryFn: bookingApi.getMy,
  })

  const cancelMutation = useMutation({
    mutationFn: bookingApi.cancel,
    onSuccess: () => {
      hapticSuccess()
      queryClient.invalidateQueries({ queryKey: ['my-bookings'] })
    },
  })

  if (isLoading) return <Spinner className="py-20" />

  const filtered = bookings?.filter(b => {
    if (filter === 'active') return ['new', 'confirmed', 'in_progress'].includes(b.status)
    if (filter === 'completed') return b.status === 'completed'
    if (filter === 'cancelled') return b.status === 'cancelled'
    return true
  })

  return (
    <div className="flex flex-col gap-4 pb-6 px-4">
      <h1 className="text-xl font-bold pt-4">Мои записи</h1>

      <div className="flex gap-2 overflow-x-auto">
        {[
          { id: 'all', label: 'Все' },
          { id: 'active', label: 'Активные' },
          { id: 'completed', label: 'Завершённые' },
          { id: 'cancelled', label: 'Отменённые' },
        ].map(f => (
          <button
            key={f.id}
            onClick={() => { haptic(); setFilter(f.id) }}
            className={`shrink-0 px-3 py-1.5 rounded-full text-sm font-medium
              ${filter === f.id ? 'bg-accent text-white' : 'bg-[var(--secondary-bg)]'}`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {filtered?.length === 0 && (
        <p className="text-center text-[var(--hint-color)] py-10">Записей не найдено</p>
      )}

      {filtered?.map(b => (
        <Card key={b.id}>
          <div className="flex justify-between items-start mb-2">
            <h3 className="font-semibold">{b.service?.name || 'Услуга'}</h3>
            <Badge className={getStatusColor(b.status)}>{getStatusLabel(b.status)}</Badge>
          </div>
          <div className="text-sm text-[var(--hint-color)] flex flex-col gap-1">
            <div>📅 {formatDate(b.date)}, {b.time_start}</div>
            {b.car_brand && <div>🚗 {b.car_brand} {b.car_model}</div>}
            {b.price_final ? (
              <div className="text-accent font-medium">💰 {formatPrice(b.price_final)}</div>
            ) : b.price_estimated ? (
              <div>💰 от {formatPrice(b.price_estimated)}</div>
            ) : null}
          </div>
          {['new', 'confirmed'].includes(b.status) && (
            <div className="mt-3">
              <Button
                variant="outline"
                size="sm"
                onClick={() => cancelMutation.mutate(b.id)}
                disabled={cancelMutation.isPending}
              >
                Отменить запись
              </Button>
            </div>
          )}
        </Card>
      ))}
    </div>
  )
}
