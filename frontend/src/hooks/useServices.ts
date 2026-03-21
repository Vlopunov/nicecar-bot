import { useQuery } from '@tanstack/react-query'
import { servicesApi } from '../api/services'

export function useServices() {
  return useQuery({
    queryKey: ['services'],
    queryFn: servicesApi.getAll,
  })
}

export function useService(id: number) {
  return useQuery({
    queryKey: ['service', id],
    queryFn: () => servicesApi.getById(id),
    enabled: !!id,
  })
}
