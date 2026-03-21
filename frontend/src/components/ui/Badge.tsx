import { ReactNode } from 'react'

interface BadgeProps {
  children: ReactNode
  className?: string
}

export function Badge({ children, className = '' }: BadgeProps) {
  return (
    <span className={`inline-block px-2.5 py-1 text-xs font-medium rounded-full ${className}`}>
      {children}
    </span>
  )
}
