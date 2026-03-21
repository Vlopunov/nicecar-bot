interface Props {
  balance: number
  cashbackPercent: number
}

export function LoyaltyCard({ balance, cashbackPercent }: Props) {
  return (
    <div className="bg-gradient-to-br from-primary to-gray-800 rounded-2xl p-5 text-white">
      <div className="text-xs uppercase tracking-wider opacity-70 mb-1">Бонусный баланс</div>
      <div className="text-3xl font-bold">{balance.toFixed(0)} <span className="text-lg">BYN</span></div>
      <div className="mt-3 flex items-center gap-2 text-sm opacity-70">
        <span>Кэшбэк {cashbackPercent}%</span>
        <span>•</span>
        <span>NiceCar Center</span>
      </div>
    </div>
  )
}
