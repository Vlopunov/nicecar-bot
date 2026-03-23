import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { adminApi } from '../../api/admin'
import { Card } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { Input, Textarea } from '../../components/ui/Input'
import { Spinner } from '../../components/ui/Spinner'
import { haptic, hapticSuccess, hapticError } from '../../utils/telegram'

const EMPTY_FORM = {
  title: '',
  description: '',
  discount_type: 'percent' as 'percent' | 'fixed' | 'gift',
  discount_value: '',
  date_start: '',
  date_end: '',
}

export function PromotionsPage() {
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(EMPTY_FORM)
  const queryClient = useQueryClient()

  const { data: promos, isLoading } = useQuery({
    queryKey: ['admin-promotions'],
    queryFn: adminApi.getPromotions,
  })

  const createMutation = useMutation({
    mutationFn: adminApi.createPromotion,
    onSuccess: () => {
      hapticSuccess()
      queryClient.invalidateQueries({ queryKey: ['admin-promotions'] })
      setForm(EMPTY_FORM)
      setShowForm(false)
    },
    onError: () => {
      hapticError()
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.title.trim() || !form.date_start || !form.date_end) return
    haptic('medium')
    createMutation.mutate({
      title: form.title.trim(),
      description: form.description.trim() || null,
      discount_type: form.discount_type,
      discount_value: form.discount_type === 'gift' ? null : Number(form.discount_value) || 0,
      date_start: form.date_start,
      date_end: form.date_end,
    })
  }

  const updateField = <K extends keyof typeof EMPTY_FORM>(key: K, value: (typeof EMPTY_FORM)[K]) => {
    setForm(prev => ({ ...prev, [key]: value }))
  }

  const discountLabel: Record<string, string> = {
    percent: '% скидка',
    fixed: 'Фикс. скидка (BYN)',
    gift: 'Подарок',
  }

  if (isLoading) return <Spinner className="py-20" />

  return (
    <div className="flex flex-col gap-4 pb-6 px-4">
      <div className="flex justify-between items-center pt-4">
        <h1 className="text-xl font-bold">Акции и промо</h1>
        <Button
          size="sm"
          variant={showForm ? 'outline' : 'primary'}
          onClick={() => {
            haptic()
            setShowForm(v => !v)
          }}
        >
          {showForm ? 'Отмена' : '+ Создать'}
        </Button>
      </div>

      {showForm && (
        <Card className="border-accent/30">
          <form onSubmit={handleSubmit} className="flex flex-col gap-3">
            <Input
              label="Название"
              placeholder="Скидка 20% на полировку"
              value={form.title}
              onChange={e => updateField('title', e.target.value)}
              required
            />
            <Textarea
              label="Описание"
              placeholder="Подробности акции..."
              value={form.description}
              onChange={e => updateField('description', e.target.value)}
            />
            <div className="flex flex-col gap-1">
              <label className="text-sm text-[var(--hint-color)]">Тип скидки</label>
              <select
                className="w-full px-4 py-3 rounded-xl bg-[var(--secondary-bg)] text-[var(--text-color)] border-none outline-none focus:ring-2 focus:ring-accent/30 transition"
                value={form.discount_type}
                onChange={e => updateField('discount_type', e.target.value as typeof form.discount_type)}
              >
                <option value="percent">Процент (%)</option>
                <option value="fixed">Фиксированная (BYN)</option>
                <option value="gift">Подарок</option>
              </select>
            </div>
            {form.discount_type !== 'gift' && (
              <Input
                label={form.discount_type === 'percent' ? 'Размер скидки (%)' : 'Размер скидки (BYN)'}
                type="number"
                min="0"
                step={form.discount_type === 'percent' ? '1' : '0.01'}
                placeholder={form.discount_type === 'percent' ? '20' : '50'}
                value={form.discount_value}
                onChange={e => updateField('discount_value', e.target.value)}
                required
              />
            )}
            <div className="grid grid-cols-2 gap-3">
              <Input
                label="Дата начала"
                type="date"
                value={form.date_start}
                onChange={e => updateField('date_start', e.target.value)}
                required
              />
              <Input
                label="Дата окончания"
                type="date"
                value={form.date_end}
                onChange={e => updateField('date_end', e.target.value)}
                required
              />
            </div>
            <Button type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Создание...' : 'Создать акцию'}
            </Button>
            {createMutation.isError && (
              <p className="text-sm text-red-500 text-center">Ошибка при создании. Попробуйте снова.</p>
            )}
          </form>
        </Card>
      )}

      {promos?.map((p: any) => (
        <Card key={p.id}>
          <div className="flex justify-between items-start mb-2">
            <h3 className="font-semibold">{p.title}</h3>
            <Badge className={p.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}>
              {p.is_active ? 'Активна' : 'Архив'}
            </Badge>
          </div>
          {p.description && <p className="text-sm text-[var(--hint-color)]">{p.description}</p>}
          <div className="flex justify-between items-center mt-2">
            <span className="text-xs text-[var(--hint-color)]">
              {p.date_start} — {p.date_end}
            </span>
            {p.discount_type && (
              <Badge className="bg-accent/10 text-accent">
                {p.discount_type === 'gift'
                  ? 'Подарок'
                  : p.discount_type === 'percent'
                    ? `${p.discount_value}%`
                    : `${p.discount_value} BYN`}
              </Badge>
            )}
          </div>
        </Card>
      ))}

      {(!promos || promos.length === 0) && !showForm && (
        <p className="text-center text-[var(--hint-color)] py-10">Акций пока нет</p>
      )}
    </div>
  )
}
