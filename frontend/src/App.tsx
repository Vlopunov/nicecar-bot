import { Routes, Route, useNavigate, useLocation } from 'react-router-dom'
import { useEffect } from 'react'
import { tg } from './utils/telegram'

// Client pages
import { HomePage } from './pages/client/HomePage'
import { ServicesPage } from './pages/client/ServicesPage'
import { ServiceDetailPage } from './pages/client/ServiceDetailPage'
import { BookingPage, BookingSuccessPage } from './pages/client/BookingPage'
import { ProfilePage } from './pages/client/ProfilePage'
import { HistoryPage } from './pages/client/HistoryPage'
import { LoyaltyPage } from './pages/client/LoyaltyPage'
import { PortfolioPage } from './pages/client/PortfolioPage'

// Admin pages
import { DashboardPage } from './pages/admin/DashboardPage'
import { BookingsPage } from './pages/admin/BookingsPage'
import { SchedulePage } from './pages/admin/SchedulePage'
import { ServicesManagePage } from './pages/admin/ServicesManagePage'
import { ClientsPage } from './pages/admin/ClientsPage'
import { ClientDetailPage } from './pages/admin/ClientDetailPage'
import { PortfolioManagePage } from './pages/admin/PortfolioManagePage'
import { PromotionsPage } from './pages/admin/PromotionsPage'
import { BroadcastPage } from './pages/admin/BroadcastPage'
import { AnalyticsPage } from './pages/admin/AnalyticsPage'

function BackButtonHandler() {
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    const isRoot = location.pathname === '/' || location.pathname === '/admin'
    if (tg?.BackButton) {
      if (isRoot) {
        tg.BackButton.hide()
      } else {
        tg.BackButton.show()
        const handler = () => navigate(-1)
        tg.BackButton.onClick(handler)
        return () => tg!.BackButton.offClick(handler)
      }
    }
  }, [location.pathname, navigate])

  return null
}

export default function App() {
  return (
    <>
      <BackButtonHandler />
      <div className="min-h-screen max-w-lg mx-auto">
        <Routes>
          {/* Client routes */}
          <Route path="/" element={<HomePage />} />
          <Route path="/services" element={<ServicesPage />} />
          <Route path="/services/:id" element={<ServiceDetailPage />} />
          <Route path="/booking" element={<BookingPage />} />
          <Route path="/booking/success" element={<BookingSuccessPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/loyalty" element={<LoyaltyPage />} />
          <Route path="/portfolio" element={<PortfolioPage />} />

          {/* Admin routes */}
          <Route path="/admin" element={<DashboardPage />} />
          <Route path="/admin/bookings" element={<BookingsPage />} />
          <Route path="/admin/schedule" element={<SchedulePage />} />
          <Route path="/admin/services" element={<ServicesManagePage />} />
          <Route path="/admin/clients" element={<ClientsPage />} />
          <Route path="/admin/clients/:id" element={<ClientDetailPage />} />
          <Route path="/admin/portfolio" element={<PortfolioManagePage />} />
          <Route path="/admin/promotions" element={<PromotionsPage />} />
          <Route path="/admin/broadcast" element={<BroadcastPage />} />
          <Route path="/admin/analytics" element={<AnalyticsPage />} />
        </Routes>
      </div>
    </>
  )
}
