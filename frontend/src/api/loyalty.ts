import { api } from './client'
import type { LoyaltyInfo } from '../types'

export const loyaltyApi = {
  get: () => api.get<LoyaltyInfo>('/api/loyalty'),
  getReferralLink: () =>
    api.get<{ link: string; referral_bonus: number; welcome_bonus: number }>('/api/loyalty/referral-link'),
}
