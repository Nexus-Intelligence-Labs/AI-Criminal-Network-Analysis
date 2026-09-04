import { createContext, useEffect, useState, type ReactNode } from 'react'
import { mockAuthService } from '../services/auth'
import type { AuthService, AuthSession, AuthStatus, LoginInput } from '../types/auth'

interface AuthContextValue {
  status: AuthStatus
  session: AuthSession | null
  isAuthenticated: boolean
  login(input: LoginInput): Promise<void>
  logout(): Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children, service = mockAuthService }: { children: ReactNode; service?: AuthService }) {
  const [status, setStatus] = useState<AuthStatus>('unauthenticated')
  const [session, setSession] = useState<AuthSession | null>(null)

  useEffect(() => {
    void service.getCurrentSession().then((currentSession) => {
      setSession(currentSession)
      setStatus(currentSession ? 'authenticated' : 'unauthenticated')
    }).catch(() => setStatus('unauthenticated'))
  }, [service])

  async function login(input: LoginInput) {
    setStatus('authenticating')
    try {
      const nextSession = await service.login(input)
      setSession(nextSession)
      setStatus('authenticated')
    } catch (error) {
      setStatus('unauthenticated')
      throw error
    }
  }

  async function logout() {
    setStatus('signing-out')
    await service.logout()
    setSession(null)
    setStatus('unauthenticated')
  }

  return <AuthContext.Provider value={{ status, session, isAuthenticated: status === 'authenticated', login, logout }}>{children}</AuthContext.Provider>
}

export { AuthContext }
