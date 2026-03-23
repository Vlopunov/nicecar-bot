import { api } from './client'
import type { DashboardData } from '../types'

export const adminApi = {
  getDashboard: () => api.get<DashboardData>('/api/admin/dashboard'),
  getBookings: (params?: string) => api.get<any[]>(`/api/admin/bookings${params ? '?' + params : ''}`),
  updateBooking: (id: number, data: any) => api.put<any>(`/api/admin/bookings/${id}`, data),
  createBooking: (data: any) => api.post<any>('/api/admin/bookings', data),
  getSchedule: (date?: string) => api.get<any>(`/api/admin/schedule${date ? '?date=' + date : ''}`),
  getUsers: (params?: string) => api.get<any[]>(`/api/admin/users${params ? '?' + params : ''}`),
  getUser: (id: number) => api.get<any>(`/api/admin/users/${id}`),
  updateUser: (id: number, data: any) => api.put<any>(`/api/admin/users/${id}`, data),
  getAnalytics: (period?: string) => api.get<any>(`/api/admin/analytics${period ? '?period=' + period : ''}`),
  getPosts: () => api.get<any[]>('/api/admin/posts'),
  getPromotions: () => api.get<any[]>('/api/admin/promotions'),
  createPromotion: (data: any) => api.post<any>('/api/admin/promotions', data),
  getBroadcasts: () => api.get<any[]>('/api/admin/broadcast'),
  createBroadcast: (data: any) => api.post<any>('/api/admin/broadcast', data),
  getCategories: () => api.get<any[]>('/api/admin/categories'),
  getServices: () => api.get<any[]>('/api/admin/services'),
  updateService: (id: number, data: any) => api.put<any>(`/api/admin/services/${id}`, data),
  getFAQ: () => api.get<any[]>('/api/admin/faq'),
  createFAQ: (data: any) => api.post<any>('/api/admin/faq', data),
  updateFAQ: (id: number, data: any) => api.put<any>(`/api/admin/faq/${id}`, data),
  deleteFAQ: (id: number) => api.delete<any>(`/api/admin/faq/${id}`),
  getPortfolio: () => api.get<any[]>('/api/admin/portfolio'),
  createPortfolio: (data: any) => api.post<any>('/api/admin/portfolio', data),
}
