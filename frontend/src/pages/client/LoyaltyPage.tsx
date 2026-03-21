import { useQuery } from '@tanstack/react-query'
import { loyaltyApi } from '../../api/loyalty'
import { LoyaltyCard } from '../../components/client/LoyaltyCard'
import { Card } from '../../components/ui/Card'
import { Spinner } from '../../components/ui/Spinner'

export function LoyaltyPage() {
  const { data: loyalty, isLoading } = useQuery({
    queryKey: ['loyalty'],
    queryFn: loyaltyApi.get,
  })

  const { data: refData } = useQuery({
    queryKey: ['referral-link'],
    queryFn: loyaltyApi.getReferralLink,
  })

  if (isLoading) return <Spinner className="py-20" />
  if (!loyalty) return null

  return (
    <div className="flex flex-col gap-4 pb-6 px-4">
      <h1 className="text-xl font-bold pt-4">Программа лояльности</h1>

      <LoyaltyCard balance={loyalty.balance} cashbackPercent={loyalty.cashback_percent} />

      {/* Info */}
      <Card>
        <h2 className="font-semibold mb-2">Как это работает</h2>
        <div className="flex flex-col gap-2 text-sm">
          <div className="flex gap-2">
            <span>💰</span>
            <span>Кэшбэк {loyalty.cashback_percent}% с каждого визита</span>
          </div>
          <div className="flex gap-2">
            <span>🛒</span>
            <span>Оплата бонусами до {loyalty.max_usage_percent}% стоимости</span>
          </div>
          <div className="flex gap-2">
            <span>⏰</span>
            <span>Бонусы сгорают через 6 месяцев неактивности</span>
          </div>
        </div>
      </Card>

      {/* Referral */}
      {refData && (
        <Card>
          <h2 className="font-semibold mb-2">Приведи друга</h2>
          <p className="text-sm text-[var(--hint-color)] mb-3">
            Вы получите <strong>{refData.referral_bonus} BYN</strong> бонусов, друг —{' '}
            <strong>{refData.welcome_bonus} BYN</strong> на первый визит!
          </p>
          <div className="bg-[var(--secondary-bg)] rounded-xl p-3 text-sm break-all">
            {refData.link}
          </div>
        </Card>
      )}

      {/* Transaction history */}
      {loyalty.transactions.length > 0 && (
        <div>
          <h2 className="font-semibold mb-3">История операций</h2>
          {loyalty.transactions.map(t => (
            <div key={t.id} className="flex justify-between items-center py-3 border-b border-[var(--secondary-bg)]">
              <div>
                <p className="text-sm font-medium">{t.description}</p>
                <p className="text-xs text-[var(--hint-color)]">
                  {t.created_at ? new Date(t.created_at).toLocaleDateString('ru') : ''}
                </p>
              </div>
              <span className={`font-bold ${t.amount > 0 ? 'text-green-600' : 'text-red-500'}`}>
                {t.amount > 0 ? '+' : ''}{t.amount.toFixed(0)} BYN
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
