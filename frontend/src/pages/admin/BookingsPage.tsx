import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { adminApi } from '../../api/admin'
import { Card } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Spinner } from '../../components/ui/Spinner'
import { formatDate, getStatusLabel, getStatusColor, formatPrice } from '../../utils/format'
import { haptic, hapticSuccess, hapticError } from '../../utils/telegram'

const EMPTY_BOOKING = {
  phone: '',
  service_id: '',
  date: '',
  time_start: '',
  car_brand: '',
  car_model: '',
  car_class: '',
  comment: '',
}

export function BookingsPage() {
  const [statusFilter, setStatusFilter] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(EMPTY_BOOKING)
  const queryClient = useQueryClient()

  const { data: bookings, isLoading } = useQuery({
    queryKey: ['admin-bookings', statusFilter],
    queryFn: () => adminApi.getBookings(statusFilter ? `status=${statusFilter}` : ''),
  })

  const { data: services } = useQuery({
    queryKey: ['admin-services'],
    queryFn: adminApi.getServices,
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => adminApi.updateBooking(id, data),
    onSuccess: () => {
      hapticSuccess()
      queryClient.invalidateQueries({ queryKey: ['admin-bookings'] })
    },
    onError: () => {
      hapticError()
    },
  })

  const createMutation = useMutation({
    mutationFn: adminApi.createBooking,
    onSuccess: () => {
      hapticSuccess()
      queryClient.invalidateQueries({ queryKey: ['admin-bookings'] })
      setForm(EMPTY_BOOKING)
      setShowForm(false)
    },
    onError: () => {
      hapticError()
    },
  })

  const handleCreateSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.phone.trim() || !form.service_id || !form.date || !form.time_start) return
    haptic('medium')
    createMutation.mutate({
      phone: form.phone.trim(),
      service_id: Number(form.service_id),
      date: form.date,
      time_start: form.time_start,
      car_brand: form.car_brand.trim() || null,
      car_model: form.car_model.trim() || null,
      car_class: form.car_class || null,
      comment: form.comment.trim() || null,
    })
  }

  const updateField = <K extends keyof typeof EMPTY_BOOKING>(key: K, value: (typeof EMPTY_BOOKING)[K]) => {
    setForm(prev => ({ ...prev, [key]: value }))
  }

  if (isLoading) return <Spinner className="py-20" />

  const statuses = ['', 'new', 'confirmed', 'in_progress', 'completed', 'cancelled']
  const activeServices = services?.filter((s: any) => s.is_active) || []

  return (
    <div className="flex flex-col gap-4 pb-6 px-4">
      <div className="flex justify-between items-center pt-4">
        <h1 className="text-xl font-bold">Управление записями</h1>
        <Button
          size="sm"
          variant={showForm ? 'outline' : 'primary'}
          onClick={() => {
            haptic()
            setShowForm(v => !v)
          }}
        >
          {showForm ? 'Отмена' : '+ Новая запись'}
        </Button>
      </div>

      {showForm && (
        <Card className="border-accent/30">
          <form onSubmit={handleCreateSubmit} className="flex flex-col gap-3">
            <h3 className="font-semibold text-sm">Ручная запись клиента</h3>
            <Input
              label="Телефон клиента"
              type="tel"
              placeholder="+375291234567"
              value={form.phone}
              onChange={e => updateField('phone', e.target.value)}
              required
            />
            <div className="flex flex-col gap-1">
              <label className="text-sm text-[var(--hint-color)]">Услуга</label>
              <select
                className="w-full px-4 py-3 rounded-xl bg-[var(--secondary-bg)] text-[var(--text-color)] border-none outline-none focus:ring-2 focus:ring-accent/30 transition"
                value={form.service_id}
                onChange={e => updateField('service_id', e.target.value)}
                required
              >
                <option value="">Выберите услугу</option>
                {activeServices.map((s: any) => (
                  <option key={s.id} value={s.id}>{s.name}</option>
                ))}
              </select>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Input
                label="Дата"
                type="date"
                value={form.date}
                onChange={e => updateField('date', e.target.value)}
                required
              />
              <Input
                label="Время начала"
                type="time"
                value={form.time_start}
                onChange={e => updateField('time_start', e.target.value)}
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Input
                label="Марка авто"
                placeholder="BMW"
                value={form.car_brand}
                onChange={e => updateField('car_brand', e.target.value)}
              />
              <Input
                label="Модель"
                placeholder="X5"
                value={form.car_model}
                onChange={e => updateField('car_model', e.target.value)}
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-sm text-[var(--hint-color)]">Класс авто</label>
              <select
                className="w-full px-4 py-3 rounded-xl bg-[var(--secondary-bg)] text-[var(--text-color)] border-none outline-none focus:ring-2 focus:ring-accent/30 transition"
                value={form.car_class}
                onChange={e => updateField('car_class', e.target.value)}
              >
                <option value="">Не указан</option>
                <option value="sedan">Седан</option>
                <option value="suv">Внедорожник / Кроссовер</option>
                <option value="minivan">Минивэн</option>
                <option value="coupe">Купе</option>
              </select>
            </div>
            <Input
              label="Комментарий"
              placeholder="Доп. пожелания клиента..."
              value={form.comment}
              onChange={e => updateField('comment', e.target.value)}
            />
            <Button type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Создание...' : 'Создать запись'}
            </Button>
            {createMutation.isError && (
              <p className="text-sm text-red-500 text-center">Ошибка при создании записи. Попробуйте снова.</p>
            )}
          </form>
        </Card>
      )}

      <div className="flex gap-2 overflow-x-auto pb-1">
        {statuses.map(s => (
          <button
            key={s}
            onClick={() => {
              haptic()
              setStatusFilter(s)
            }}
            className={`shrink-0 px-3 py-1.5 rounded-full text-sm font-medium transition-colors
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
