import { NavLink } from 'react-router-dom'
import { 
  LayoutDashboard, 
  FolderOpen, 
  Search, 
  Users, 
  Network, 
  Clock, 
  FileText, 
  AlertCircle, 
  BarChart3, 
  Settings,
  LogOut,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAuth } from '@/context/useAuth'
import { useNavigate } from 'react-router-dom'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard, section: 'overview' },
  { name: 'Cases', href: '/cases', icon: FolderOpen, section: 'investigation' },
  { name: 'Search', href: '/search', icon: Search, section: 'investigation' },
  { name: 'Entities', href: '/entities', icon: Users, section: 'investigation' },
  { name: 'Graph', href: '/graph', icon: Network, section: 'investigation' },
  { name: 'Timeline', href: '/timeline', icon: Clock, section: 'investigation' },
  { name: 'Evidence', href: '/evidence', icon: FileText, section: 'investigation' },
  { name: 'Alerts', href: '/alerts', icon: AlertCircle, section: 'analysis' },
  { name: 'Analytics', href: '/analytics', icon: BarChart3, section: 'analysis' },
  { name: 'Settings', href: '/settings', icon: Settings, section: 'system' },
]

const sections = [
  { id: 'overview', title: 'OVERVIEW' },
  { id: 'investigation', title: 'INVESTIGATION' },
  { id: 'analysis', title: 'ANALYSIS' },
  { id: 'system', title: 'SYSTEM' },
]

export function Sidebar() {
  const { session, logout } = useAuth()
  const navigate = useNavigate()

  async function signOut() {
    await logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="flex flex-col w-64 bg-card border-r h-full">
      {/* Logo */}
      <div className="px-6 py-4 border-b">
        <h1 className="text-lg font-bold">Criminal Network</h1>
        <p className="text-xs text-muted-foreground">Intelligence Platform</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4">
        {sections.map((section) => (
          <div key={section.id} className="mb-4">
            <div className="px-6 mb-2">
              <h3 className="text-xs font-semibold text-muted-foreground">
                {section.title}
              </h3>
            </div>
            {navigation
              .filter((item) => item.section === section.id)
              .map((item) => (
                <NavLink
                  key={item.name}
                  to={item.href}
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-3 px-6 py-2 text-sm transition-fast',
                      isActive
                        ? 'bg-primary text-primary-foreground'
                        : 'text-foreground hover:bg-accent'
                    )
                  }
                >
                  <item.icon className="h-4 w-4" />
                  {item.name}
                </NavLink>
              ))}
          </div>
        ))}
      </nav>

      {/* Demo Badge */}
      <div className="px-6 py-4 border-t space-y-3">
        <div className="px-3 text-xs text-muted-foreground truncate">
          {session?.user.displayName}
        </div>
        <button
          type="button"
          className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm text-foreground hover:bg-accent"
          onClick={signOut}
        >
          <LogOut className="h-4 w-4" />
          Sign out
        </button>
        <div className="px-3 py-2 bg-muted rounded-md text-xs text-center">
          <span className="font-semibold">DEMO MODE</span>
        </div>
      </div>
    </div>
  )
}
