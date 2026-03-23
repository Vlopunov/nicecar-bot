import { useQuery } from '@tanstack/react-query'
import { userApi } from '../api/user'
import type { ReactNode } from 'react'

interface AdminGuardProps {
  children: ReactNode
}

export function AdminGuard({ children }: AdminGuardProps) {
  const { data: user, isLoading, isError } = useQuery({
    queryKey: ['me'],
    queryFn: () => userApi.getMe(),
    staleTime: 5 * 60 * 1000,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary border-t-transparent" />
      </div>
    )
  }

  if (isError || !user?.is_admin) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center p-6">
          <div className="text-4xl mb-4">🔒</div>
          <h1 className="text-xl font-semibold mb-2">Access Denied</h1>
          <p className="text-gray-500">You do not have admin privileges.</p>
        </div>
      </div>
    )
  }

  return <>{children}</>
}
