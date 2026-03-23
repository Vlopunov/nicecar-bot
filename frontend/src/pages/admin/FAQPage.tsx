import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { adminApi } from '../../api/admin'
import { Card } from '../../components/ui/Card'
import { Button } from '../../components/ui/Button'
import { Spinner } from '../../components/ui/Spinner'
import { Input, Textarea } from '../../components/ui/Input'
import { haptic, hapticSuccess, hapticError, tg } from '../../utils/telegram'

interface FAQItem {
  id: number
  category: string
  question: string
  answer: string
}

interface FAQFormData {
  category: string
  question: string
  answer: string
}

const emptyForm: FAQFormData = { category: '', question: '', answer: '' }

export function FAQPage() {
  const queryClient = useQueryClient()
  const [form, setForm] = useState<FAQFormData>(emptyForm)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [expandedId, setExpandedId] = useState<number | null>(null)

  const { data: faqItems, isLoading } = useQuery({
    queryKey: ['admin-faq'],
    queryFn: adminApi.getFAQ,
  })

  const createMutation = useMutation({
    mutationFn: adminApi.createFAQ,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-faq'] })
      setForm(emptyForm)
      hapticSuccess()
    },
    onError: () => hapticError(),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: FAQFormData }) =>
      adminApi.updateFAQ(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-faq'] })
      setEditingId(null)
      setForm(emptyForm)
      hapticSuccess()
    },
    onError: () => hapticError(),
  })

  const deleteMutation = useMutation({
    mutationFn: adminApi.deleteFAQ,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-faq'] })
      hapticSuccess()
    },
    onError: () => hapticError(),
  })

  const handleSubmit = () => {
    if (!form.category.trim() || !form.question.trim() || !form.answer.trim()) return
    haptic('medium')
    if (editingId !== null) {
      updateMutation.mutate({ id: editingId, data: form })
    } else {
      createMutation.mutate(form)
    }
  }

  const handleEdit = (item: FAQItem) => {
    haptic()
    setEditingId(item.id)
    setForm({ category: item.category, question: item.question, answer: item.answer })
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleCancelEdit = () => {
    haptic()
    setEditingId(null)
    setForm(emptyForm)
  }

  const handleDelete = (item: FAQItem) => {
    haptic('medium')
    tg?.showConfirm(
      `Удалить вопрос "${item.question}"?`,
      (ok: boolean) => {
        if (ok) deleteMutation.mutate(item.id)
      }
    )
  }

  const toggleExpand = (id: number) => {
    haptic()
    setExpandedId(expandedId === id ? null : id)
  }

  // Group FAQ items by category
  const grouped = (faqItems ?? []).reduce<Record<string, FAQItem[]>>((acc, item: FAQItem) => {
    const cat = item.category || 'Без категории'
    if (!acc[cat]) acc[cat] = []
    acc[cat].push(item)
    return acc
  }, {})

  const categories = Object.keys(grouped).sort()

  if (isLoading) return <Spinner className="py-20" />

  const isFormValid = form.category.trim() && form.question.trim() && form.answer.trim()
  const isPending = createMutation.isPending || updateMutation.isPending

  return (
    <div className="flex flex-col gap-4 pb-6 px-4">
      <h1 className="text-xl font-bold pt-4">FAQ</h1>

      {/* Create / Edit form */}
      <Card>
        <h2 className="font-semibold mb-3">
          {editingId !== null ? 'Редактировать вопрос' : 'Новый вопрос'}
        </h2>

        <div className="flex flex-col gap-3">
          <Input
            label="Категория"
            placeholder="Например: Услуги, Цены, Общее..."
            value={form.category}
            onChange={e => setForm(f => ({ ...f, category: e.target.value }))}
          />
          <Input
            label="Вопрос"
            placeholder="Вопрос клиента..."
            value={form.question}
            onChange={e => setForm(f => ({ ...f, question: e.target.value }))}
          />
          <Textarea
            label="Ответ"
            placeholder="Ответ на вопрос..."
            value={form.answer}
            onChange={e => setForm(f => ({ ...f, answer: e.target.value }))}
          />
        </div>

        <div className="flex gap-2 mt-3">
          <Button
            className="flex-1"
            disabled={!isFormValid || isPending}
            onClick={handleSubmit}
          >
            {isPending
              ? 'Сохранение...'
              : editingId !== null
                ? 'Сохранить'
                : 'Добавить'}
          </Button>
          {editingId !== null && (
            <Button variant="ghost" onClick={handleCancelEdit}>
              Отмена
            </Button>
          )}
        </div>
      </Card>

      {/* FAQ list grouped by category */}
      {categories.length === 0 && (
        <p className="text-sm text-[var(--hint-color)] text-center py-8">
          Вопросов пока нет. Добавьте первый вопрос выше.
        </p>
      )}

      {categories.map(category => (
        <div key={category} className="flex flex-col gap-2">
          <h2 className="font-semibold text-sm text-accent uppercase tracking-wide mt-2">
            {category}
            <span className="ml-2 text-[var(--hint-color)] text-xs font-normal normal-case">
              ({grouped[category].length})
            </span>
          </h2>

          {grouped[category].map((item: FAQItem) => (
            <Card key={item.id}>
              <div
                className="flex justify-between items-start gap-2 cursor-pointer"
                onClick={() => toggleExpand(item.id)}
              >
                <p className="text-sm font-medium flex-1">{item.question}</p>
                <svg
                  className={`w-4 h-4 shrink-0 text-[var(--hint-color)] transition-transform duration-200 mt-0.5 ${
                    expandedId === item.id ? 'rotate-180' : ''
                  }`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>

              {expandedId === item.id && (
                <div className="mt-3">
                  <p className="text-sm text-[var(--hint-color)] whitespace-pre-wrap">
                    {item.answer}
                  </p>
                  <div className="flex gap-2 mt-3 pt-3 border-t border-[var(--secondary-bg)]">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleEdit(item)
                      }}
                    >
                      Редактировать
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-red-500"
                      disabled={deleteMutation.isPending}
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDelete(item)
                      }}
                    >
                      Удалить
                    </Button>
                  </div>
                </div>
              )}
            </Card>
          ))}
        </div>
      ))}
    </div>
  )
}
