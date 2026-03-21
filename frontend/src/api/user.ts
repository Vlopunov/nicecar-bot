import { api } from './client'
import type { UserProfile } from '../types'

export const userApi = {
  getMe: () => api.get<UserProfile>('/api/user/me'),
  updateMe: (data: { phone?: string; first_name?: string; last_name?: string }) =>
    api.put<UserProfile>('/api/user/me', data),
}
