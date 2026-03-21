import { create } from 'zustand'
import type { UserProfile } from '../types'

interface AuthState {
  user: UserProfile | null
  isAdmin: boolean
  setUser: (user: UserProfile) => void
  setAdmin: (isAdmin: boolean) => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAdmin: false,
  setUser: (user) => set({ user }),
  setAdmin: (isAdmin) => set({ isAdmin }),
}))
