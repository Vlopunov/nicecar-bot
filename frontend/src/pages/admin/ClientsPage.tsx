import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { adminApi } from '../../api/admin'
import { Card } from '../../components/ui/Card'
import { Input } from '../../components/ui/Input'
import { Spinner } from '../../components/ui/Spinner'
import { haptic } from '../../utils/telegram'

export function ClientsPage() {
  const [search, setSearch] = useState('')
  const navigate = useNavigate()

  const { data: users, isLoading } = useQuery({
    queryKey: ['admin-users', search],
    queryFn: () => adminApi.getUsers(search ? `search=${encodeURIComponent(search)}` : ''),
  })

  if (isLoading) return <Spinner className="py-20" />

  return (
    <div className="flex flex-col gap-4 pb-6 px-4">
      <h1 className="text-xl font-bold pt-4">База клиентов</h1>

      <Input placeholder="Поиск по имени, телефону..." value={search}
        onChange={e => setSearch(e.target.value)} />

      <p className="text-sm text-[var(--hint-color)]">Всего: {users?.length || 0} клиентов</p>

      {users?.map((u: any) => (
        <Card key={u.id} onClick={() => { haptic(); navigate(`/admin/clients/${u.id}`) }}>
          <div className="flex justify-between items-start">
            <div>
              <h3 className="font-semibold">{u.first_name} {u.last_name || ''}</h3>
              <p className="text-sm text-[var(--hint-color)]">
                {u.username ? `@${u.username}` : ''} {u.phone || ''}
              </p>
            </div>
            <div className="text-right">
              <div className="text-sm font-medium">{u.visit_count} визитов</div>
              <div className="text-xs text-[var(--hint-color)]">{u.total_spent.toFixed(0)} BYN</div>
            </div>
          </div>
          {u.tags && (
            <div className="flex gap-1 mt-2">
              {u.tags.split(',').map((tag: string) => (
                <span key={tag} className="text-xs bg-accent/10 text-accent px-2 py-0.5 rounded-full">
                  {tag.trim()}
                </span>
              ))}
            </div>
          )}
        </Card>
      ))}
    </div>
  )
}
