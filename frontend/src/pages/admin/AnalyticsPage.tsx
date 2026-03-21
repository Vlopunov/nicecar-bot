import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { adminApi } from '../../api/admin'
import { Card } from '../../components/ui/Card'
import { Spinner } from '../../components/ui/Spinner'
import { formatPrice } from '../../utils/format'

export function AnalyticsPage() {
  const [period, setPeriod] = useState('month')

  const { data, isLoading } = useQuery({
    queryKey: ['admin-analytics', period],
    queryFn: () => adminApi.getAnalytics(period),
  })

  if (isLoading) return <Spinner className="py-20" />
  if (!data) return null

  return (
    <div className="flex flex-col gap-4 pb-6 px-4">
      <h1 className="text-xl font-bold pt-4">Аналитика</h1>

      <div className="flex gap-2">
        {['week', 'month', 'year'].map(p => (
          <button
            key={p}
            onClick={() => setPeriod(p)}
            className={`px-4 py-2 rounded-full text-sm font-medium
              ${period === p ? 'bg-accent text-white' : 'bg-[var(--secondary-bg)]'}`}
          >
            {p === 'week' ? 'Неделя' : p === 'month' ? 'Месяц' : 'Год'}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-3">
        <Card className="text-center">
          <div className="text-2xl font-bold">{data.total_bookings}</div>
          <div className="text-xs text-[var(--hint-color)]">Всего записей</div>
        </Card>
        <Card className="text-center">
          <div className="text-2xl font-bold text-green-600">{data.completed_bookings}</div>
          <div className="text-xs text-[var(--hint-color)]">Завершено</div>
        </Card>
        <Card className="text-center">
          <div className="text-2xl font-bold text-red-500">{data.cancelled_bookings}</div>
          <div className="text-xs text-[var(--hint-color)]">Отменено</div>
        </Card>
        <Card className="text-center">
          <div className="text-2xl font-bold text-accent">{formatPrice(data.total_revenue)}</div>
          <div className="text-xs text-[var(--hint-color)]">Выручка</div>
        </Card>
      </div>

      <Card>
        <div className="flex justify-between items-center">
          <span className="text-[var(--hint-color)]">Средний чек</span>
          <span className="text-xl font-bold">{formatPrice(data.average_check)}</span>
        </div>
      </Card>

      <div className="text-xs text-[var(--hint-color)] text-center">
        Период: {data.date_from} — {data.date_to}
      </div>
    </div>
  )
}
