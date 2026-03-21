import { api } from './client'
import type { Booking } from '../types'

export interface CreateBookingData {
  service_id: number
  car_brand: string
  car_model: string
  car_class?: string | null
  date: string
  time: string
  notes?: string | null
  bonus_used?: number
}

export const bookingApi = {
  create: (data: CreateBookingData) => api.post<Booking>('/api/bookings', data),
  getMy: () => api.get<Booking[]>('/api/bookings/my'),
  cancel: (id: number) => api.put<Booking>(`/api/bookings/${id}/cancel`),
}

export const slotsApi = {
  get: (date: string, serviceId: number) =>
    api.get<{ date: string; service_id: number; slots: string[] }>(
      `/api/slots?date=${date}&service_id=${serviceId}`
    ),
}
