import { AuthError, type AuthService, type AuthSession, type LoginInput } from '../../types/auth'

const SESSION_KEY = 'cna-development-session'

// DEVELOPMENT ONLY: replace this adapter with the FastAPI service before production use.
export const mockAuthService: AuthService = {
  async login(input: LoginInput) {
    await delay(650)
    if (!input.email || !input.password) {
      throw new AuthError('invalid-credentials', 'Unable to sign in. Check your credentials and try again.')
    }
    const session: AuthSession = {
      user: { id: 'development-user', displayName: input.email.split('@')[0], email: input.email },
      issuedAt: new Date().toISOString(),
    }
    const storage = input.remember ? localStorage : sessionStorage
    storage.setItem(SESSION_KEY, JSON.stringify(session))
    return session
  },
  async logout() {
    await delay(180)
    localStorage.removeItem(SESSION_KEY)
    sessionStorage.removeItem(SESSION_KEY)
  },
  async getCurrentSession() {
    const raw = localStorage.getItem(SESSION_KEY) ?? sessionStorage.getItem(SESSION_KEY)
    return raw ? (JSON.parse(raw) as AuthSession) : null
  },
  async requestPasswordReset(email: string) {
    await delay(500)
    if (!email) throw new AuthError('unexpected', 'We could not process that request. Please try again.')
  },
  async resetPassword(password: string) {
    await delay(500)
    if (!password) throw new AuthError('unexpected', 'We could not update your password. Please try again.')
  },
  async requestAccess(input) {
    await delay(500)
    if (!input.name || !input.email || !input.reason) throw new AuthError('unexpected', 'Please complete the required fields.')
  },
}

function delay(milliseconds: number) {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds))
}
