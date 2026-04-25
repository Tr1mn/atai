import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Profile from './pages/Profile'
import Matching from './pages/Matching'
import Packages from './pages/Packages'
import PackageDetail from './pages/PackageDetail'
import Booking from './pages/Booking'
import MyBookings from './pages/MyBookings'
import Trips from './pages/Trips'
import TripDetail from './pages/TripDetail'
import PartnerDashboard from './pages/PartnerDashboard'
import AdminDashboard from './pages/AdminDashboard'
import BecomePartner from './pages/BecomePartner'
import TravelRequestForm from './pages/TravelRequestForm'
import MyTravelRequests from './pages/MyTravelRequests'
import PartnerRequests from './pages/PartnerRequests'
import Individual from './pages/Individual'
import AIAssistant from './pages/AIAssistant'

function PrivateRoute({ children, role }) {
  const { user, loading } = useAuth()
  // Wait for the initial /api/auth/me call to resolve before redirecting.
  // Without this, a refresh would briefly redirect authenticated users to /login.
  if (loading) return null
  if (!user) return <Navigate to="/login" replace />
  if (role && user.role !== role && user.role !== 'admin') return <Navigate to="/" replace />
  return children
}

function AppRoutes() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/ai-assistant" element={<AIAssistant />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/packages" element={<Packages />} />
          <Route path="/packages/:id" element={<PackageDetail />} />
          <Route path="/packages/:id/book" element={<PrivateRoute><Booking /></PrivateRoute>} />
          <Route path="/trips" element={<PrivateRoute><Trips /></PrivateRoute>} />
          <Route path="/trips/:id" element={<PrivateRoute><TripDetail /></PrivateRoute>} />
          <Route path="/individual" element={<PrivateRoute><Individual /></PrivateRoute>} />
          <Route path="/matching" element={<PrivateRoute><Matching /></PrivateRoute>} />
          <Route path="/profile" element={<PrivateRoute><Profile /></PrivateRoute>} />
          <Route path="/my-bookings" element={<PrivateRoute><MyBookings /></PrivateRoute>} />
          <Route path="/travel-request" element={<PrivateRoute><TravelRequestForm /></PrivateRoute>} />
          <Route path="/my-requests" element={<PrivateRoute><MyTravelRequests /></PrivateRoute>} />
          <Route path="/become-partner" element={<PrivateRoute><BecomePartner /></PrivateRoute>} />
          <Route path="/partner" element={<PrivateRoute role="partner"><PartnerDashboard /></PrivateRoute>} />
          <Route path="/partner/requests" element={<PrivateRoute role="partner"><PartnerRequests /></PrivateRoute>} />
          <Route path="/admin" element={<PrivateRoute role="admin"><AdminDashboard /></PrivateRoute>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <Footer />
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}
