export type AuthStatus = 'unauthenticated' | 'authenticating' | 'authenticated' | 'signing-out' | 'session-expired'

export interface AuthUser {
  id: string
  displayName: string
  email: string
}

export interface AuthSession {
  user: AuthUser
  issuedAt: string
}

export interface LoginInput {
  email: string
  password: string
  remember: boolean
}

export type AuthErrorCode = 'invalid-credentials' | 'network' | 'unavailable' | 'unexpected'

export class AuthError extends Error {
  constructor(public readonly code: AuthErrorCode, message: string) {
    super(message)
    this.name = 'AuthError'
  }
}

export interface AuthService {
  login(input: LoginInput): Promise<AuthSession>
  logout(): Promise<void>
  getCurrentSession(): Promise<AuthSession | null>
  requestPasswordReset(email: string): Promise<void>
  resetPassword(password: string, token?: string): Promise<void>
  requestAccess(input: { name: string; organization: string; email: string; reason: string }): Promise<void>
}
