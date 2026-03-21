import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { adminApi } from '../../api/admin'
import { Card } from '../../components/ui/Card'
import { Button } from '../../components/ui/Button'
import { Badge } from '../../components/ui/Badge'
import { Spinner } from '../../components/ui/Spinner'
import { Textarea } from '../../components/ui/Input'

export function BroadcastPage() {
  const [text, setText] = useState('')
  const [segment, setSegment] = useState('all')
  const queryClient = useQueryClient()

  const { data: broadcasts, isLoading } = useQuery({
    queryKey: ['admin-broadcasts'],
    queryFn: adminApi.getBroadcasts,
  })

  const createMutation = useMutation({
    mutationFn: adminApi.createBroadcast,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-broadcasts'] })
      setText('')
    },
  })

  if (isLoading) return <Spinner className="py-20" />

  const segments = [
    { id: 'all', label: 'Все' },
    { id: 'recent', label: 'Недавние' },
    { id: 'inactive', label: 'Неактивные' },
    { id: 'vip', label: 'VIP' },
  ]

  return (
    <div className="flex flex-col gap-4 pb-6 px-4">
      <h1 className="text-xl font-bold pt-4">Рассылки</h1>

      <Card>
        <h2 className="font-semibold mb-3">Новая рассылка</h2>
        <Textarea placeholder="Текст рассылки (HTML)..." value={text}
          onChange={e => setText(e.target.value)} />

        <div className="flex gap-2 mt-3 flex-wrap">
          {segments.map(s => (
            <button
              key={s.id}
              onClick={() => setSegment(s.id)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium
                ${segment === s.id ? 'bg-accent text-white' : 'bg-[var(--secondary-bg)]'}`}
            >
              {s.label}
            </button>
          ))}
        </div>

        <Button
          className="w-full mt-3"
          disabled={!text.trim() || createMutation.isPending}
          onClick={() => createMutation.mutate({ text, segment })}
        >
          Создать рассылку
        </Button>
      </Card>

      <h2 className="font-semibold">История рассылок</h2>
      {broadcasts?.map((b: any) => (
        <Card key={b.id}>
          <div className="flex justify-between items-start mb-1">
            <p className="text-sm font-medium line-clamp-2">{b.text}</p>
            <Badge className={
              b.status === 'sent' ? 'bg-green-100 text-green-700' :
              b.status === 'sending' ? 'bg-yellow-100 text-yellow-700' :
              'bg-gray-100 text-gray-600'
            }>
              {b.status}
            </Badge>
          </div>
          <div className="text-xs text-[var(--hint-color)] mt-1">
            Отправлено: {b.total_sent} | Ошибки: {b.total_errors}
          </div>
        </Card>
      ))}
    </div>
  )
}
