import { api } from './client'
import type { ServiceCategory, Service } from '../types'

export const servicesApi = {
  getAll: () => api.get<ServiceCategory[]>('/api/services'),
  getById: (id: number) => api.get<Service>(`/api/services/${id}`),
}
