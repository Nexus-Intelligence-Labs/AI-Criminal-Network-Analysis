import { AuthError, type AuthService } from '../../types/auth'

const TOKEN_KEY = 'cna-api-access-token'
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export const apiAuthService: AuthService = {
  async login(input) {
    let response: Response
    try {
      response = await fetch(`${apiBaseUrl}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: input.email.trim(), password: input.password }),
      })
    } catch {
      throw new AuthError('network', 'Authentication service is unavailable.')
    }
    const payload = await response.json().catch(() => null)
    if (!response.ok || !payload?.success || !payload.access_token) {
      throw new AuthError('invalid-credentials', 'Unable to sign in. Check your credentials and try again.')
    }
    const storage = input.remember ? localStorage : sessionStorage
    storage.setItem(TOKEN_KEY, payload.access_token)
    return {
      user: { id: String(payload.user_id), displayName: input.email.trim(), email: input.email.trim() },
      issuedAt: new Date().toISOString(),
      accessToken: payload.access_token,
    }
  },
  async logout() {
    localStorage.removeItem(TOKEN_KEY)
    sessionStorage.removeItem(TOKEN_KEY)
  },
  async getCurrentSession() {
    const token = localStorage.getItem(TOKEN_KEY) ?? sessionStorage.getItem(TOKEN_KEY)
    return token ? {
      user: { id: 'api-user', displayName: 'Authenticated user', email: '' },
      issuedAt: new Date().toISOString(),
      accessToken: token,
    } : null
  },
  async requestPasswordReset() { throw new AuthError('unavailable', 'Password reset is not available through the API yet.') },
  async resetPassword() { throw new AuthError('unavailable', 'Password reset is not available through the API yet.') },
  async requestAccess() { throw new AuthError('unavailable', 'Access requests are not available through the API yet.') },
}

export function getApiAccessToken() {
  return localStorage.getItem(TOKEN_KEY) ?? sessionStorage.getItem(TOKEN_KEY)
}
