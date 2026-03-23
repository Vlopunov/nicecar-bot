export interface ServiceCategory {
  id: number
  name: string
  icon: string
  description: string | null
  services: Service[]
}

export interface Service {
  id: number
  category_id?: number
  name: string
  description: string | null
  duration_min_hours: number
  duration_max_hours: number
  has_car_classes: boolean
  is_package: boolean
  image_url: string | null
  prices: ServicePrice[]
}

export interface ServicePrice {
  id: number
  car_class: string | null
  package_name: string | null
  price_from: number
  price_to: number | null
  description: string | null
}

export interface Booking {
  id: number
  service: { id: number; name: string } | null
  car_brand: string
  car_model: string
  car_class: string | null
  date: string
  time_start: string
  time_end: string
  status: string
  price_estimated: number | null
  price_final: number | null
  notes: string | null
  bonus_used: number
  bonus_earned: number
  created_at: string | null
}

export interface UserProfile {
  id: number
  telegram_id: number
  username: string | null
  first_name: string
  last_name: string | null
  phone: string | null
  bonus_balance: number
  total_spent: number
  visit_count: number
  tags: string | null
  is_admin: boolean
  created_at: string | null
}

export interface LoyaltyInfo {
  balance: number
  cashback_percent: number
  max_usage_percent: number
  transactions: BonusTransaction[]
}

export interface BonusTransaction {
  id: number
  amount: number
  type: string
  description: string
  created_at: string | null
}

export interface PortfolioItem {
  id: number
  image_url: string
  image_before_url: string | null
  car_brand: string | null
  car_model: string | null
  description: string | null
  category_id: number | null
  created_at: string | null
}

export interface FAQCategory {
  category: string
  items: FAQItem[]
}

export interface FAQItem {
  id: number
  question: string
  answer: string
}

export interface Promotion {
  id: number
  title: string
  description: string | null
  discount_type: string
  discount_value: number | null
  image_url: string | null
  date_end: string
}

export interface DashboardData {
  today_bookings: number
  tomorrow_bookings: number
  revenue_today: number
  revenue_week: number
  revenue_month: number
  new_clients_week: number
  posts_load_percent: number
  today_by_status: Record<string, number>
}
