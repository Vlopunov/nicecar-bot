import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { adminApi } from '../../api/admin'
import { Card } from '../../components/ui/Card'
import { Spinner } from '../../components/ui/Spinner'
import { formatPrice } from '../../utils/format'

export function DashboardPage() {
  const navigate = useNavigate()
  const { data, isLoading } = useQuery({
    queryKey: ['admin-dashboard'],
    queryFn: adminApi.getDashboard,
    refetchInterval: 30000,
  })

  if (isLoading) return <Spinner className="py-20" />
  if (!data) return null

  return (
    <div className="flex flex-col gap-4 pb-6 px-4">
      <h1 className="text-xl font-bold pt-4">Панель управления</h1>

      <div className="grid grid-cols-2 gap-3">
        <Card className="text-center">
          <div className="text-3xl font-bold">{data.today_bookings}</div>
          <div className="text-xs text-[var(--hint-color)]">Записей сегодня</div>
        </Card>
        <Card className="text-center">
          <div className="text-3xl font-bold">{data.tomorrow_bookings}</div>
          <div className="text-xs text-[var(--hint-color)]">Записей завтра</div>
        </Card>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <Card className="text-center">
          <div className="text-lg font-bold text-accent">{formatPrice(data.revenue_today)}</div>
          <div className="text-xs text-[var(--hint-color)]">Сегодня</div>
        </Card>
        <Card className="text-center">
          <div className="text-lg font-bold text-accent">{formatPrice(data.revenue_week)}</div>
          <div className="text-xs text-[var(--hint-color)]">За неделю</div>
        </Card>
        <Card className="text-center">
          <div className="text-lg font-bold text-accent">{formatPrice(data.revenue_month)}</div>
          <div className="text-xs text-[var(--hint-color)]">За месяц</div>
        </Card>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <Card className="text-center">
          <div className="text-xl font-bold">{data.new_clients_week}</div>
          <div className="text-xs text-[var(--hint-color)]">Новых за неделю</div>
        </Card>
        <Card className="text-center">
          <div className="text-xl font-bold">{data.posts_load_percent}%</div>
          <div className="text-xs text-[var(--hint-color)]">Загрузка постов</div>
        </Card>
      </div>

      {/* Quick navigation */}
      <div className="flex flex-col gap-2 mt-2">
        {[
          { path: '/admin/bookings', label: 'Управление записями', icon: '📋' },
          { path: '/admin/schedule', label: 'Расписание', icon: '📅' },
          { path: '/admin/clients', label: 'База клиентов', icon: '👥' },
          { path: '/admin/services', label: 'Управление услугами', icon: '🔧' },
          { path: '/admin/portfolio', label: 'Портфолио', icon: '📸' },
          { path: '/admin/promotions', label: 'Акции', icon: '🎁' },
          { path: '/admin/broadcast', label: 'Рассылки', icon: '📢' },
          { path: '/admin/analytics', label: 'Аналитика', icon: '📊' },
        ].map(item => (
          <button
            key={item.path}
            onClick={() => navigate(item.path)}
            className="flex items-center gap-3 p-4 bg-[var(--secondary-bg)] rounded-xl text-left w-full"
          >
            <span>{item.icon}</span>
            <span className="font-medium">{item.label}</span>
            <span className="ml-auto text-[var(--hint-color)]">→</span>
          </button>
        ))}
      </div>
    </div>
  )
}
