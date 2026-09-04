import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { DashboardShell } from './App'
import { AuthProvider } from './context/AuthContext'
import { ThemeProvider } from './context/ThemeContext'
import { RequireAuth } from './routes/RequireAuth'
import { AccessRequest, ForgotPassword, ResetPassword, SessionExpired, Unauthorized } from './pages/AuthPages'
import { Login } from './pages/Login'
import { Alerts } from './pages/Alerts'
import { Analytics } from './pages/Analytics'
import { Cases } from './pages/Cases'
import { Dashboard } from './pages/Dashboard'
import { Entities } from './pages/Entities'
import { EntityDetail } from './pages/EntityDetail'
import { Evidence } from './pages/Evidence'
import { GraphPage } from './pages/GraphPage'
import { Search } from './pages/Search'
import { Settings } from './pages/Settings'
import { Timeline } from './pages/Timeline'
import { Investigations } from './pages/Investigations'
import { ReviewQueues } from './pages/ReviewQueues'
import { SavedQueries } from './pages/SavedQueries'
import { AlertRules } from './pages/AlertRules'
import './styles.css'
import './dashboard.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            <Route path="/access-request" element={<AccessRequest />} />
            <Route path="/session-expired" element={<SessionExpired />} />
            <Route path="/unauthorized" element={<Unauthorized />} />
            <Route element={<RequireAuth />}>
              <Route element={<DashboardShell />}>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/cases" element={<Cases />} />
                <Route path="/search" element={<Search />} />
                <Route path="/entities" element={<Entities />} />
                <Route path="/entities/:entityId" element={<EntityDetail />} />
                <Route path="/graph" element={<GraphPage />} />
                <Route path="/timeline" element={<Timeline />} />
                <Route path="/evidence" element={<Evidence />} />
                <Route path="/alerts" element={<Alerts />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="/investigations" element={<Investigations />} />
                <Route path="/reviews" element={<ReviewQueues />} />
                <Route path="/saved-queries" element={<SavedQueries />} />
                <Route path="/alert-rules" element={<AlertRules />} />
              </Route>
            </Route>
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  </StrictMode>,
)
