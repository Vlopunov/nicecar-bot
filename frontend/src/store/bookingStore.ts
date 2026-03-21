import { create } from 'zustand'

interface BookingState {
  serviceId: number | null
  serviceName: string
  carClass: string | null
  carBrand: string
  carModel: string
  date: string
  time: string
  notes: string
  bonusUsed: number
  step: number
  setService: (id: number, name: string) => void
  setCarClass: (cls: string | null) => void
  setCar: (brand: string, model: string) => void
  setDate: (date: string) => void
  setTime: (time: string) => void
  setNotes: (notes: string) => void
  setBonusUsed: (amount: number) => void
  setStep: (step: number) => void
  reset: () => void
}

const initial = {
  serviceId: null,
  serviceName: '',
  carClass: null,
  carBrand: '',
  carModel: '',
  date: '',
  time: '',
  notes: '',
  bonusUsed: 0,
  step: 1,
}

export const useBookingStore = create<BookingState>((set) => ({
  ...initial,
  setService: (id, name) => set({ serviceId: id, serviceName: name }),
  setCarClass: (cls) => set({ carClass: cls }),
  setCar: (brand, model) => set({ carBrand: brand, carModel: model }),
  setDate: (date) => set({ date, time: '' }),
  setTime: (time) => set({ time }),
  setNotes: (notes) => set({ notes }),
  setBonusUsed: (amount) => set({ bonusUsed: amount }),
  setStep: (step) => set({ step }),
  reset: () => set(initial),
}))
