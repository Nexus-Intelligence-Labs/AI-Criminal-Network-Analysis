import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../context/useAuth'

export function RequireAuth() {
  const { status } = useAuth()
  const location = useLocation()
  if (status === 'authenticating') return <main className="loading-screen" aria-live="polite">Checking session...</main>
  if (status !== 'authenticated') return <Navigate to="/login" replace state={{ from: `${location.pathname}${location.search}` }} />
  return <Outlet />
}
