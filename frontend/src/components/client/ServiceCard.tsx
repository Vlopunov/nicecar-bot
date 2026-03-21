import { useNavigate } from 'react-router-dom'
import { Card } from '../ui/Card'
import { haptic } from '../../utils/telegram'
import { formatPrice } from '../../utils/format'
import type { Service } from '../../types'

interface Props {
  service: Service
}

export function ServiceCard({ service }: Props) {
  const navigate = useNavigate()
  const minPrice = service.prices.length > 0 ? Math.min(...service.prices.map(p => p.price_from)) : null

  return (
    <Card
      className="flex flex-col gap-2"
      onClick={() => {
        haptic()
        navigate(`/services/${service.id}`)
      }}
    >
      <h3 className="font-semibold text-base">{service.name}</h3>
      {service.description && (
        <p className="text-sm text-[var(--hint-color)] line-clamp-2">{service.description}</p>
      )}
      <div className="flex items-center justify-between mt-1">
        <span className="text-accent font-bold">
          {minPrice ? `от ${formatPrice(minPrice)}` : 'по запросу'}
        </span>
        <span className="text-xs text-[var(--hint-color)]">
          {service.duration_min_hours === service.duration_max_hours
            ? `${service.duration_min_hours} ч`
            : `${service.duration_min_hours}—${service.duration_max_hours} ч`}
        </span>
      </div>
    </Card>
  )
}
