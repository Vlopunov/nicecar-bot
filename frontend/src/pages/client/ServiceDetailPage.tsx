import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { servicesApi } from '../../api/services'
import { Button } from '../../components/ui/Button'
import { Spinner } from '../../components/ui/Spinner'
import { formatPrice } from '../../utils/format'
import { haptic } from '../../utils/telegram'
import { useBookingStore } from '../../store/bookingStore'

export function ServiceDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const setService = useBookingStore(s => s.setService)

  const { data: service, isLoading } = useQuery({
    queryKey: ['service', id],
    queryFn: () => servicesApi.getById(Number(id)),
    enabled: !!id,
  })

  if (isLoading) return <Spinner className="py-20" />
  if (!service) return <p className="p-4">Услуга не найдена</p>

  const handleBook = () => {
    haptic('medium')
    setService(service.id, service.name)
    navigate('/booking')
  }

  return (
    <div className="flex flex-col gap-4 pb-6 px-4">
      <h1 className="text-xl font-bold pt-4">{service.name}</h1>

      {service.description && (
        <p className="text-[var(--hint-color)]">{service.description}</p>
      )}

      {/* Prices */}
      <div className="bg-[var(--secondary-bg)] rounded-2xl p-4">
        <h2 className="font-semibold mb-3">Цены</h2>
        {service.is_package ? (
          <div className="flex flex-col gap-3">
            {service.prices.map(p => (
              <div key={p.id} className="flex flex-col gap-1">
                <div className="flex justify-between items-center">
                  <span className="font-medium">{p.package_name || 'Стандарт'}</span>
                  <span className="text-accent font-bold">от {formatPrice(p.price_from)}</span>
                </div>
                {p.description && (
                  <p className="text-sm text-[var(--hint-color)]">{p.description}</p>
                )}
              </div>
            ))}
          </div>
        ) : service.has_car_classes ? (
          <div className="flex flex-col gap-2">
            {service.prices.map(p => (
              <div key={p.id} className="flex justify-between">
                <span>{p.car_class ? `${p.car_class} класс` : 'Общая'}</span>
                <span className="font-bold text-accent">от {formatPrice(p.price_from)}</span>
              </div>
            ))}
          </div>
        ) : service.prices.length > 0 ? (
          <p className="text-accent font-bold text-lg">от {formatPrice(service.prices[0].price_from)}</p>
        ) : (
          <p>Цена по запросу</p>
        )}
      </div>

      {/* Duration */}
      <div className="bg-[var(--secondary-bg)] rounded-2xl p-4">
        <h2 className="font-semibold mb-1">Время выполнения</h2>
        <p>
          {service.duration_min_hours === service.duration_max_hours
            ? `${service.duration_min_hours} ч`
            : `от ${service.duration_min_hours} до ${service.duration_max_hours} ч`
          }
        </p>
      </div>

      <Button onClick={handleBook} className="w-full" size="lg">
        📅 Записаться
      </Button>
    </div>
  )
}
