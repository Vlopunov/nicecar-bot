import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { adminApi } from '../../api/admin'
import { Spinner } from '../../components/ui/Spinner'
import { getStatusColor } from '../../utils/format'

export function SchedulePage() {
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0])

  const { data, isLoading } = useQuery({
    queryKey: ['admin-schedule', selectedDate],
    queryFn: () => adminApi.getSchedule(selectedDate),
  })

  const hours = Array.from({ length: 11 }, (_, i) => `${(9 + i).toString().padStart(2, '0')}:00`)

  if (isLoading) return <Spinner className="py-20" />

  return (
    <div className="flex flex-col gap-4 pb-6 px-4">
      <h1 className="text-xl font-bold pt-4">Расписание</h1>

      <input
        type="date"
        value={selectedDate}
        onChange={e => setSelectedDate(e.target.value)}
        className="px-4 py-3 rounded-xl bg-[var(--secondary-bg)] text-[var(--text-color)]"
      />

      {data?.schedule?.map((post: any) => (
        <div key={post.post.id ?? 'unassigned'} className="bg-[var(--secondary-bg)] rounded-2xl p-4">
          <h3 className="font-semibold mb-3">{post.post.name}</h3>

          <div className="relative" style={{ height: `${hours.length * 48}px` }}>
            {/* Time grid */}
            {hours.map((h, i) => (
              <div
                key={h}
                className="absolute left-0 right-0 border-t border-gray-200 flex items-start"
                style={{ top: `${i * 48}px`, height: '48px' }}
              >
                <span className="text-xs text-[var(--hint-color)] w-12 shrink-0 pt-1">{h}</span>
              </div>
            ))}

            {/* Bookings */}
            {post.bookings.map((b: any) => {
              const startH = parseInt(b.time_start.split(':')[0])
              const startM = parseInt(b.time_start.split(':')[1])
              const endH = parseInt(b.time_end.split(':')[0])
              const endM = parseInt(b.time_end.split(':')[1])
              const top = (startH - 9) * 48 + (startM / 60) * 48
              const height = ((endH - startH) * 60 + (endM - startM)) / 60 * 48

              return (
                <div
                  key={b.id}
                  className={`absolute left-14 right-2 rounded-lg px-2 py-1 text-xs ${getStatusColor(b.status)} overflow-hidden`}
                  style={{ top: `${top}px`, height: `${Math.max(height, 24)}px` }}
                >
                  <div className="font-medium truncate">{b.car}</div>
                  <div>{b.time_start}—{b.time_end}</div>
                </div>
              )
            })}
          </div>
        </div>
      ))}
    </div>
  )
}
