import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { adminApi } from '../../api/admin'
import { Card } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { Spinner } from '../../components/ui/Spinner'
import { formatDate, getStatusLabel, getStatusColor, formatPrice } from '../../utils/format'

export function BookingsPage() {
  const [statusFilter, setStatusFilter] = useState('')
  const queryClient = useQueryClient()

  const { data: bookings, isLoading } = useQuery({
    queryKey: ['admin-bookings', statusFilter],
    queryFn: () => adminApi.getBookings(statusFilter ? `status=${statusFilter}` : ''),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => adminApi.updateBooking(id, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-bookings'] }),
  })

  if (isLoading) return <Spinner className="py-20" />

  const statuses = ['', 'new', 'confirmed', 'in_progress', 'completed', 'cancelled']

  return (
    <div className="flex flex-col gap-4 pb-6 px-4">
      <h1 className="text-xl font-bold pt-4">Управление записями</h1>

      <div className="flex gap-2 overflow-x-auto pb-1">
        {statuses.map(s => (
          <button
            key={s}
            onClick={() => setStatusFilter(s)}
            className={`shrink-0 px-3 py-1.5 rounded-full text-sm font-medium
              ${statusFilter === s ? 'bg-accent text-white' : 'bg-[var(--secondary-bg)]'}`}
          >
            {s ? getStatusLabel(s) : 'Все'}
          </button>
        ))}
      </div>

      {bookings?.map((b: any) => (
        <Card key={b.id}>
          <div className="flex justify-between items-start mb-2">
            <div>
              <h3 className="font-semibold">{b.service?.name || 'Услуга'}</h3>
              <p className="text-sm text-[var(--hint-color)]">
                {b.user?.first_name} {b.user?.last_name}
                {b.user?.username ? ` (@${b.user.username})` : ''}
              </p>
            </div>
            <Badge className={getStatusColor(b.status)}>{getStatusLabel(b.status)}</Badge>
          </div>
          <div className="text-sm text-[var(--hint-color)] flex flex-col gap-1 mb-3">
            <div>📅 {formatDate(b.date)}, {b.time_start}—{b.time_end}</div>
            <div>🚗 {b.car_brand} {b.car_model} {b.car_class ? `(${b.car_class})` : ''}</div>
            {b.user?.phone && <div>📱 {b.user.phone}</div>}
            {b.post && <div>📌 {b.post.name}</div>}
            {b.price_estimated && <div>💰 от {formatPrice(b.price_estimated)}</div>}
          </div>

          <div className="flex gap-2 flex-wrap">
            {b.status === 'new' && (
              <>
                <Button size="sm" onClick={() => updateMutation.mutate({ id: b.id, data: { status: 'confirmed' } })}>
                  ✅ Подтвердить
                </Button>
                <Button size="sm" variant="outline" onClick={() => updateMutation.mutate({ id: b.id, data: { status: 'cancelled' } })}>
                  ❌ Отклонить
                </Button>
              </>
            )}
            {b.status === 'confirmed' && (
              <Button size="sm" onClick={() => updateMutation.mutate({ id: b.id, data: { status: 'in_progress' } })}>
                🔧 В работу
              </Button>
            )}
            {b.status === 'in_progress' && (
              <Button size="sm" onClick={() => updateMutation.mutate({ id: b.id, data: { status: 'completed' } })}>
                🎉 Завершить
              </Button>
            )}
          </div>
        </Card>
      ))}

      {bookings?.length === 0 && (
        <p className="text-center text-[var(--hint-color)] py-10">Записей не найдено</p>
      )}
    </div>
  )
}
