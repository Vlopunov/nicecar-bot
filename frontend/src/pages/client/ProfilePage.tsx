import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { userApi } from '../../api/user'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Card } from '../../components/ui/Card'
import { Spinner } from '../../components/ui/Spinner'
import { hapticSuccess } from '../../utils/telegram'

export function ProfilePage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [editing, setEditing] = useState(false)
  const [phone, setPhone] = useState('')
  const [firstName, setFirstName] = useState('')

  const { data: user, isLoading } = useQuery({
    queryKey: ['user'],
    queryFn: userApi.getMe,
  })

  const updateMutation = useMutation({
    mutationFn: userApi.updateMe,
    onSuccess: () => {
      hapticSuccess()
      setEditing(false)
      queryClient.invalidateQueries({ queryKey: ['user'] })
    },
  })

  if (isLoading) return <Spinner className="py-20" />
  if (!user) return <p className="p-4">Не удалось загрузить профиль</p>

  const handleEdit = () => {
    setPhone(user.phone || '')
    setFirstName(user.first_name)
    setEditing(true)
  }

  const handleSave = () => {
    updateMutation.mutate({ phone, first_name: firstName })
  }

  return (
    <div className="flex flex-col gap-4 pb-6 px-4">
      <h1 className="text-xl font-bold pt-4">Личный кабинет</h1>

      {editing ? (
        <Card>
          <div className="flex flex-col gap-3">
            <Input label="Имя" value={firstName} onChange={e => setFirstName(e.target.value)} />
            <Input label="Телефон" value={phone} onChange={e => setPhone(e.target.value)}
              placeholder="+375 29 XXX-XX-XX" />
            <div className="flex gap-2">
              <Button onClick={handleSave} disabled={updateMutation.isPending}>Сохранить</Button>
              <Button variant="ghost" onClick={() => setEditing(false)}>Отмена</Button>
            </div>
          </div>
        </Card>
      ) : (
        <Card>
          <div className="flex flex-col gap-2">
            <div className="flex justify-between">
              <span className="text-[var(--hint-color)]">Имя</span>
              <span className="font-medium">{user.first_name} {user.last_name || ''}</span>
            </div>
            {user.username && (
              <div className="flex justify-between">
                <span className="text-[var(--hint-color)]">Telegram</span>
                <span>@{user.username}</span>
              </div>
            )}
            <div className="flex justify-between">
              <span className="text-[var(--hint-color)]">Телефон</span>
              <span>{user.phone || 'Не указан'}</span>
            </div>
            <Button variant="ghost" size="sm" onClick={handleEdit}>Редактировать</Button>
          </div>
        </Card>
      )}

      {/* Stats */}
      <div className="grid grid-cols-3 gap-3">
        <Card className="text-center">
          <div className="text-2xl font-bold">{user.visit_count}</div>
          <div className="text-xs text-[var(--hint-color)]">Визиты</div>
        </Card>
        <Card className="text-center">
          <div className="text-2xl font-bold text-accent">{user.bonus_balance.toFixed(0)}</div>
          <div className="text-xs text-[var(--hint-color)]">Бонусы</div>
        </Card>
        <Card className="text-center">
          <div className="text-2xl font-bold">{user.total_spent.toFixed(0)}</div>
          <div className="text-xs text-[var(--hint-color)]">Потрачено</div>
        </Card>
      </div>

      {/* Navigation */}
      {[
        { path: '/history', label: 'История записей', icon: '📄' },
        { path: '/loyalty', label: 'Программа лояльности', icon: '💰' },
        { path: '/booking', label: 'Новая запись', icon: '📅' },
      ].map(item => (
        <button
          key={item.path}
          onClick={() => navigate(item.path)}
          className="flex items-center gap-3 p-4 bg-[var(--secondary-bg)] rounded-xl text-left w-full"
        >
          <span>{item.icon}</span>
          <span className="font-medium">{item.label}</span>
          <span className="ml-auto text-[var(--hint-color)]">→</span>
        </button>
      ))}
    </div>
  )
}
