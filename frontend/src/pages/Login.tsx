import { useState, type FormEvent } from 'react'
import { Eye, EyeOff, ArrowRight } from 'lucide-react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { AuthLayout } from '../components/auth/AuthLayout'
import { Alert } from '../components/ui/Alert'
import { Button } from '../components/ui/Button'
import { Card, CardContent } from '../components/ui/Card'
import { Checkbox } from '../components/ui/Checkbox'
import { Input } from '../components/ui/Input'
import { Label } from '../components/ui/Label'
import { useAuth } from '../context/useAuth'
import { AuthError } from '../types/auth'

export function Login() {
  const { login, status } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [remember, setRemember] = useState(true)
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [fieldErrors, setFieldErrors] = useState<{ email?: string; password?: string }>({})
  const busy = status === 'authenticating'

  async function submit(event: FormEvent) {
    event.preventDefault()
    const nextErrors: typeof fieldErrors = {}
    if (!email.trim()) nextErrors.email = 'Enter your email address.'
    else if (!/^\S+@\S+\.\S+$/.test(email)) nextErrors.email = 'Enter a valid email address.'
    if (!password) nextErrors.password = 'Enter your password.'
    setFieldErrors(nextErrors)
    setError('')
    if (Object.keys(nextErrors).length) return
    try {
      await login({ email: email.trim(), password, remember })
      const destination = (location.state as { from?: string } | null)?.from
      navigate(destination?.startsWith('/') ? destination : '/dashboard', { replace: true })
    } catch (reason) {
      setError(reason instanceof AuthError && reason.code === 'unavailable' ? 'Authentication service is currently unavailable.' : 'Unable to sign in. Check your credentials and try again.')
    }
  }

  return <AuthLayout title="Sign in to your workspace" description="Use your authorized work account to continue."><Card><CardContent><form onSubmit={submit} noValidate><div className="field"><Label htmlFor="email">Work email</Label><Input id="email" type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} aria-invalid={Boolean(fieldErrors.email)} aria-describedby={fieldErrors.email ? 'email-error' : undefined} placeholder="analyst@agency.org" />{fieldErrors.email && <span className="field-error" id="email-error">{fieldErrors.email}</span>}</div><div className="field"><Label htmlFor="password">Password</Label><div className="password-wrap"><Input id="password" type={showPassword ? 'text' : 'password'} autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} aria-invalid={Boolean(fieldErrors.password)} aria-describedby={fieldErrors.password ? 'password-error' : undefined} /> <button className="icon-button" type="button" onClick={() => setShowPassword(!showPassword)} aria-label={showPassword ? 'Hide password' : 'Show password'}>{showPassword ? <EyeOff size={17} /> : <Eye size={17} />}</button></div>{fieldErrors.password && <span className="field-error" id="password-error">{fieldErrors.password}</span>}</div>{error && <Alert className="alert-error">{error}</Alert>}<div className="form-row"><label className="check-label"><Checkbox checked={remember} onCheckedChange={(checked) => setRemember(checked === true)} /> Remember session</label><Link to="/forgot-password">Forgot password?</Link></div><Button className="submit-button" type="submit" disabled={busy}>{busy ? 'Signing in...' : <>Sign in <ArrowRight size={17} /></>}</Button></form><div className="divider"><span>New to the platform?</span></div><Link className="secondary-action" to="/access-request">Request controlled access <ArrowRight size={16} /></Link></CardContent></Card><p className="legal-copy">Access is monitored and limited to authorized investigative use.</p></AuthLayout>
}
