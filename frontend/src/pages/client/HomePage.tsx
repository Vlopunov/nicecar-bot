import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Button } from '../../components/ui/Button'
import { Card } from '../../components/ui/Card'
import { haptic } from '../../utils/telegram'
import { api } from '../../api/client'
import type { Promotion } from '../../types'

export function HomePage() {
  const navigate = useNavigate()
  const { data: promotions } = useQuery({
    queryKey: ['promotions'],
    queryFn: () => api.get<Promotion[]>('/api/promotions/active'),
  })

  return (
    <div className="flex flex-col gap-5 pb-6">
      {/* Header */}
      <div className="text-center pt-6 pb-2">
        <h1 className="text-2xl font-bold">NiceCar Center</h1>
        <p className="text-[var(--hint-color)] text-sm mt-1">Детейлинг центр Krytex • Минск</p>
      </div>

      {/* Promo banner */}
      {promotions && promotions.length > 0 && (
        <div className="bg-gradient-to-r from-accent to-red-700 rounded-2xl p-4 text-white mx-4">
          <p className="text-xs uppercase tracking-wider opacity-80">Акция</p>
          <p className="font-bold mt-1">{promotions[0].title}</p>
          {promotions[0].description && (
            <p className="text-sm opacity-90 mt-1 line-clamp-2">{promotions[0].description}</p>
          )}
        </div>
      )}

      {/* Quick actions */}
      <div className="grid grid-cols-3 gap-3 px-4">
        <button
          onClick={() => { haptic('medium'); navigate('/booking') }}
          className="flex flex-col items-center gap-2 p-4 bg-accent/10 rounded-2xl"
        >
          <span className="text-2xl">📅</span>
          <span className="text-xs font-medium">Записаться</span>
        </button>
        <button
          onClick={() => { haptic(); navigate('/services') }}
          className="flex flex-col items-center gap-2 p-4 bg-[var(--secondary-bg)] rounded-2xl"
        >
          <span className="text-2xl">📋</span>
          <span className="text-xs font-medium">Услуги</span>
        </button>
        <button
          onClick={() => { haptic(); navigate('/history') }}
          className="flex flex-col items-center gap-2 p-4 bg-[var(--secondary-bg)] rounded-2xl"
        >
          <span className="text-2xl">📄</span>
          <span className="text-xs font-medium">Мои записи</span>
        </button>
      </div>

      {/* Contacts */}
      <Card className="mx-4">
        <div className="flex flex-col gap-2 text-sm">
          <div className="flex items-center gap-2">
            <span>📍</span>
            <span>ул. Петруся Бровки 30, К.11</span>
          </div>
          <div className="flex items-center gap-2">
            <span>📞</span>
            <a href="tel:+375296649487" className="text-[var(--link-color)]">+375 (29) 664-94-87</a>
          </div>
          <div className="flex items-center gap-2">
            <span>🕐</span>
            <span>ПН-ПТ: 9-19, СБ: 9-18</span>
          </div>
        </div>
      </Card>

      {/* Navigation */}
      <div className="flex flex-col gap-2 px-4">
        {[
          { path: '/portfolio', icon: '📸', label: 'Наши работы' },
          { path: '/loyalty', icon: '💰', label: 'Программа лояльности' },
          { path: '/profile', icon: '👤', label: 'Личный кабинет' },
        ].map(item => (
          <button
            key={item.path}
            onClick={() => { haptic(); navigate(item.path) }}
            className="flex items-center gap-3 p-4 bg-[var(--secondary-bg)] rounded-xl text-left w-full"
          >
            <span className="text-xl">{item.icon}</span>
            <span className="font-medium">{item.label}</span>
            <span className="ml-auto text-[var(--hint-color)]">→</span>
          </button>
        ))}
      </div>
    </div>
  )
}
