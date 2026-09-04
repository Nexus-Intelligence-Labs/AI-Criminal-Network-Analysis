import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { ThemeProvider } from './context/ThemeContext'
import { RequireAuth } from './routes/RequireAuth'
import { AccessRequest, ForgotPassword, ResetPassword, SessionExpired, Unauthorized } from './pages/AuthPages'
import { Login } from './pages/Login'
import { Workspace } from './pages/Workspace'
import './styles.css'

createRoot(document.getElementById('root')!).render(<StrictMode><BrowserRouter><ThemeProvider><AuthProvider><Routes><Route path="/login" element={<Login />} /><Route path="/forgot-password" element={<ForgotPassword />} /><Route path="/reset-password" element={<ResetPassword />} /><Route path="/access-request" element={<AccessRequest />} /><Route path="/session-expired" element={<SessionExpired />} /><Route path="/unauthorized" element={<Unauthorized />} /><Route element={<RequireAuth />}><Route path="/dashboard" element={<Workspace />} /><Route path="/cases/*" element={<Workspace />} /><Route path="/search" element={<Workspace />} /><Route path="/entities/*" element={<Workspace />} /><Route path="/graph" element={<Workspace />} /><Route path="/timeline" element={<Workspace />} /><Route path="/evidence" element={<Workspace />} /><Route path="/alerts" element={<Workspace />} /><Route path="/analytics" element={<Workspace />} /><Route path="/settings" element={<Workspace />} /></Route><Route path="*" element={<Navigate to="/dashboard" replace />} /></Routes></AuthProvider></ThemeProvider></BrowserRouter></StrictMode>)
