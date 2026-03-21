import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { servicesApi } from '../../api/services'
import { bookingApi, slotsApi, CreateBookingData } from '../../api/booking'
import { useBookingStore } from '../../store/bookingStore'
import { Button } from '../../components/ui/Button'
import { Input, Textarea } from '../../components/ui/Input'
import { BookingCalendar } from '../../components/client/BookingCalendar'
import { TimeSlotPicker } from '../../components/client/TimeSlotPicker'
import { CarClassSelector } from '../../components/client/CarClassSelector'
import { Spinner } from '../../components/ui/Spinner'
import { formatPrice, formatDateFull } from '../../utils/format'
import { haptic, hapticSuccess, hapticError } from '../../utils/telegram'

export function BookingPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const store = useBookingStore()

  const { data: categories } = useQuery({
    queryKey: ['services'],
    queryFn: servicesApi.getAll,
  })

  const selectedService = categories
    ?.flatMap(c => c.services)
    .find(s => s.id === store.serviceId)

  const { data: slotsData, isLoading: slotsLoading } = useQuery({
    queryKey: ['slots', store.date, store.serviceId],
    queryFn: () => slotsApi.get(store.date, store.serviceId!),
    enabled: !!store.date && !!store.serviceId,
  })

  const createMutation = useMutation({
    mutationFn: (data: CreateBookingData) => bookingApi.create(data),
    onSuccess: () => {
      hapticSuccess()
      store.reset()
      navigate('/booking/success')
    },
    onError: () => hapticError(),
  })

  // Pre-select service from URL param
  useEffect(() => {
    const serviceId = searchParams.get('service')
    if (serviceId && !store.serviceId) {
      const svc = categories?.flatMap(c => c.services).find(s => s.id === Number(serviceId))
      if (svc) store.setService(svc.id, svc.name)
    }
  }, [searchParams, categories])

  const handleSubmit = () => {
    if (!store.serviceId || !store.date || !store.time) return
    createMutation.mutate({
      service_id: store.serviceId,
      car_brand: store.carBrand,
      car_model: store.carModel,
      car_class: store.carClass,
      date: store.date,
      time: store.time,
      notes: store.notes || null,
      bonus_used: store.bonusUsed,
    })
  }

  return (
    <div className="flex flex-col gap-4 pb-6 px-4">
      <h1 className="text-xl font-bold pt-4">Онлайн-запись</h1>

      {/* Step 1: Service selection */}
      {!store.serviceId ? (
        <div>
          <h2 className="font-semibold mb-3">Выберите услугу</h2>
          {categories?.map(cat => (
            <div key={cat.id} className="mb-4">
              <p className="text-sm text-[var(--hint-color)] mb-2">{cat.icon} {cat.name}</p>
              {cat.services.map(s => (
                <button
                  key={s.id}
                  onClick={() => { haptic(); store.setService(s.id, s.name); store.setStep(2) }}
                  className="w-full text-left p-3 bg-[var(--secondary-bg)] rounded-xl mb-1.5 flex justify-between items-center"
                >
                  <span className="font-medium">{s.name}</span>
                  <span className="text-sm text-accent">
                    {s.prices.length > 0 ? `от ${s.prices[0].price_from} BYN` : ''}
                  </span>
                </button>
              ))}
            </div>
          ))}
        </div>
      ) : (
        <>
          {/* Selected service summary */}
          <div className="bg-accent/5 border border-accent/20 rounded-xl p-3 flex justify-between items-center">
            <div>
              <p className="font-semibold">{store.serviceName}</p>
              {selectedService?.prices[0] && (
                <p className="text-sm text-accent">от {formatPrice(selectedService.prices[0].price_from)}</p>
              )}
            </div>
            <button onClick={() => { store.setService(0 as any, ''); store.reset() }}
              className="text-sm text-[var(--hint-color)]">Изменить</button>
          </div>

          {/* Step 2: Car info */}
          {selectedService?.has_car_classes && (
            <div>
              <h2 className="font-semibold mb-2">Класс автомобиля</h2>
              <CarClassSelector selected={store.carClass} onSelect={store.setCarClass} />
            </div>
          )}

          <div className="flex gap-2">
            <Input label="Марка авто" placeholder="BMW" value={store.carBrand}
              onChange={e => store.setCar(e.target.value, store.carModel)} />
            <Input label="Модель" placeholder="X5" value={store.carModel}
              onChange={e => store.setCar(store.carBrand, e.target.value)} />
          </div>

          {/* Step 3: Date & Time */}
          <h2 className="font-semibold">Дата</h2>
          <BookingCalendar selectedDate={store.date} onSelect={store.setDate} />

          {store.date && (
            <>
              <h2 className="font-semibold">Время — {formatDateFull(store.date)}</h2>
              <TimeSlotPicker
                slots={slotsData?.slots || []}
                selected={store.time}
                onSelect={store.setTime}
                loading={slotsLoading}
              />
            </>
          )}

          <Textarea label="Пожелания" placeholder="Дополнительные пожелания..."
            value={store.notes} onChange={e => store.setNotes(e.target.value)} />

          {/* Step 4: Confirm */}
          {store.date && store.time && (
            <div className="bg-[var(--secondary-bg)] rounded-2xl p-4">
              <h2 className="font-semibold mb-3">Подтверждение</h2>
              <div className="flex flex-col gap-1.5 text-sm">
                <div className="flex justify-between">
                  <span className="text-[var(--hint-color)]">Услуга</span>
                  <span className="font-medium">{store.serviceName}</span>
                </div>
                {store.carBrand && (
                  <div className="flex justify-between">
                    <span className="text-[var(--hint-color)]">Авто</span>
                    <span>{store.carBrand} {store.carModel}</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-[var(--hint-color)]">Дата</span>
                  <span>{formatDateFull(store.date)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[var(--hint-color)]">Время</span>
                  <span>{store.time}</span>
                </div>
              </div>
            </div>
          )}

          <Button
            onClick={handleSubmit}
            disabled={!store.date || !store.time || !store.carBrand || createMutation.isPending}
            className="w-full"
            size="lg"
          >
            {createMutation.isPending ? 'Отправка...' : '✅ Подтвердить запись'}
          </Button>

          {createMutation.isError && (
            <p className="text-red-500 text-center text-sm">
              {(createMutation.error as Error).message || 'Ошибка создания записи'}
            </p>
          )}
        </>
      )}
    </div>
  )
}

// Success page
export function BookingSuccessPage() {
  const navigate = useNavigate()
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4 px-4 text-center">
      <div className="text-6xl">🎉</div>
      <h1 className="text-2xl font-bold">Запись создана!</h1>
      <p className="text-[var(--hint-color)]">
        Менеджер подтвердит вашу запись в ближайшее время.
        Вы получите уведомление в боте.
      </p>
      <div className="flex gap-3 mt-4">
        <Button onClick={() => navigate('/history')}>Мои записи</Button>
        <Button variant="secondary" onClick={() => navigate('/')}>На главную</Button>
      </div>
    </div>
  )
}
