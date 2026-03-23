import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { adminApi } from '../../api/admin'
import { Card } from '../../components/ui/Card'
import { Button } from '../../components/ui/Button'
import { Input, Textarea } from '../../components/ui/Input'
import { Spinner } from '../../components/ui/Spinner'
import { haptic, hapticSuccess, hapticError } from '../../utils/telegram'

const EMPTY_FORM = {
  image_url: '',
  image_before_url: '',
  car_brand: '',
  car_model: '',
  description: '',
  category_id: '',
}

export function PortfolioManagePage() {
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(EMPTY_FORM)
  const queryClient = useQueryClient()

  const { data: items, isLoading } = useQuery({
    queryKey: ['admin-portfolio'],
    queryFn: adminApi.getPortfolio,
  })

  const { data: categories } = useQuery({
    queryKey: ['admin-categories'],
    queryFn: adminApi.getCategories,
  })

  const createMutation = useMutation({
    mutationFn: adminApi.createPortfolio,
    onSuccess: () => {
      hapticSuccess()
      queryClient.invalidateQueries({ queryKey: ['admin-portfolio'] })
      setForm(EMPTY_FORM)
      setShowForm(false)
    },
    onError: () => {
      hapticError()
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.image_url.trim() || !form.car_brand.trim() || !form.car_model.trim()) return
    haptic('medium')
    createMutation.mutate({
      image_url: form.image_url.trim(),
      image_before_url: form.image_before_url.trim() || null,
      car_brand: form.car_brand.trim(),
      car_model: form.car_model.trim(),
      description: form.description.trim() || null,
      category_id: form.category_id ? Number(form.category_id) : null,
    })
  }

  const updateField = <K extends keyof typeof EMPTY_FORM>(key: K, value: (typeof EMPTY_FORM)[K]) => {
    setForm(prev => ({ ...prev, [key]: value }))
  }

  if (isLoading) return <Spinner className="py-20" />

  return (
    <div className="flex flex-col gap-4 pb-6 px-4">
      <div className="flex justify-between items-center pt-4">
        <h1 className="text-xl font-bold">Управление портфолио</h1>
        <Button
          size="sm"
          variant={showForm ? 'outline' : 'primary'}
          onClick={() => {
            haptic()
            setShowForm(v => !v)
          }}
        >
          {showForm ? 'Отмена' : '+ Добавить'}
        </Button>
      </div>

      {showForm && (
        <Card className="border-accent/30">
          <form onSubmit={handleSubmit} className="flex flex-col gap-3">
            <Input
              label="URL изображения (после)"
              placeholder="https://example.com/photo.jpg"
              value={form.image_url}
              onChange={e => updateField('image_url', e.target.value)}
              required
            />
            <Input
              label="URL изображения (до) — необязательно"
              placeholder="https://example.com/before.jpg"
              value={form.image_before_url}
              onChange={e => updateField('image_before_url', e.target.value)}
            />
            <div className="grid grid-cols-2 gap-3">
              <Input
                label="Марка авто"
                placeholder="BMW"
                value={form.car_brand}
                onChange={e => updateField('car_brand', e.target.value)}
                required
              />
              <Input
                label="Модель"
                placeholder="X5"
                value={form.car_model}
                onChange={e => updateField('car_model', e.target.value)}
                required
              />
            </div>
            <Textarea
              label="Описание"
              placeholder="Полировка кузова, керамическое покрытие..."
              value={form.description}
              onChange={e => updateField('description', e.target.value)}
            />
            {categories && categories.length > 0 && (
              <div className="flex flex-col gap-1">
                <label className="text-sm text-[var(--hint-color)]">Категория</label>
                <select
                  className="w-full px-4 py-3 rounded-xl bg-[var(--secondary-bg)] text-[var(--text-color)] border-none outline-none focus:ring-2 focus:ring-accent/30 transition"
                  value={form.category_id}
                  onChange={e => updateField('category_id', e.target.value)}
                >
                  <option value="">Без категории</option>
                  {categories.map((c: any) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>
            )}
            <Button type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Добавление...' : 'Добавить в портфолио'}
            </Button>
            {createMutation.isError && (
              <p className="text-sm text-red-500 text-center">Ошибка при добавлении. Попробуйте снова.</p>
            )}
          </form>
        </Card>
      )}

      <div className="grid grid-cols-2 gap-3">
        {items?.map((item: any) => (
          <Card key={item.id} className="p-2">
            <div className="aspect-square rounded-xl overflow-hidden mb-2">
              <img src={item.image_url} alt="" className="w-full h-full object-cover" loading="lazy" />
            </div>
            <p className="text-xs font-medium">{item.car_brand} {item.car_model}</p>
            {item.description && (
              <p className="text-xs text-[var(--hint-color)] line-clamp-2 mt-0.5">{item.description}</p>
            )}
            <p className="text-xs text-[var(--hint-color)] mt-0.5">
              {item.is_visible ? '👁 Видимо' : '🚫 Скрыто'}
            </p>
          </Card>
        ))}
      </div>

      {(!items || items.length === 0) && !showForm && (
        <p className="text-center text-[var(--hint-color)] py-10">Портфолио пусто</p>
      )}
    </div>
  )
}
