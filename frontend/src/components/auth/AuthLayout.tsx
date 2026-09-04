import { Moon, ShieldCheck, Sun } from 'lucide-react'
import type { ReactNode } from 'react'
import { Button } from '../ui/Button'
import { useTheme } from '../../context/useTheme'

export function AuthLayout({ children, title, description, eyebrow = 'Secure investigator access' }: { children: ReactNode; title: string; description?: string; eyebrow?: string }) {
  const { theme, toggleTheme } = useTheme()
  const nextTheme = theme === 'dark' ? 'light' : 'dark'
  return <main className="auth-page"><div className="auth-grid" /><div className="auth-brand"><div className="auth-brand-top"><span className="brand-rule" aria-hidden="true" /><Button className="theme-toggle" type="button" onClick={toggleTheme} aria-label={`Switch to ${nextTheme} theme`} title={`Switch to ${nextTheme} theme`}>{theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}</Button></div><div><h1>AI-Powered Criminal<br />Network Analysis System</h1><p className="brand-copy">A focused workspace for connecting evidence, entities, and relationships across complex investigations.</p></div><div className="brand-foot"><ShieldCheck size={16} /> Controlled access for investigative teams</div></div><div className="auth-panel"><div className="auth-panel-inner"><p className="eyebrow">{eyebrow}</p><h2>{title}</h2>{description && <p className="auth-description">{description}</p>}{children}<p className="dev-note">Development frontend · Backend authentication pending</p></div></div></main>
}
