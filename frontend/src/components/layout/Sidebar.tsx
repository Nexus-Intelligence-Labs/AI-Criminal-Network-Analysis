import { useState } from 'react'
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
  BriefcaseBusiness,
  ScanSearch,
  Bookmark,
  BellRing,
  PanelLeftClose,
  PanelLeftOpen,
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
  { name: 'Investigations', href: '/investigations', icon: BriefcaseBusiness, section: 'investigation' },
  { name: 'Timeline', href: '/timeline', icon: Clock, section: 'investigation' },
  { name: 'Evidence', href: '/evidence', icon: FileText, section: 'investigation' },
  { name: 'Alerts', href: '/alerts', icon: AlertCircle, section: 'analysis' },
  { name: 'Analytics', href: '/analytics', icon: BarChart3, section: 'analysis' },
  { name: 'AI Review', href: '/reviews', icon: ScanSearch, section: 'analysis' },
  { name: 'Saved Queries', href: '/saved-queries', icon: Bookmark, section: 'analysis' },
  { name: 'Alert Rules', href: '/alert-rules', icon: BellRing, section: 'analysis' },
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
  const [collapsed, setCollapsed] = useState(false)

  async function signOut() {
    await logout()
    navigate('/login', { replace: true })
  }

  return (
    <aside className={cn('app-sidebar flex flex-col bg-card border-r h-full', collapsed && 'is-collapsed')}>
      <div className="sidebar-brand px-4 py-4 border-b">
        <div className="brand-mark"><Network className="h-4 w-4" /></div>
        <div className="sidebar-brand-copy">
          <h1 className="text-sm font-bold tracking-tight">CNA / INTELLIGENCE</h1>
          <p className="text-[10px] text-muted-foreground uppercase tracking-[0.18em]">Investigation workspace</p>
        </div>
        <button
          type="button"
          className="sidebar-toggle ml-auto"
          onClick={() => setCollapsed((value) => !value)}
          aria-label={collapsed ? 'Expand navigation' : 'Collapse navigation'}
          title={collapsed ? 'Expand navigation' : 'Collapse navigation'}
        >
          {collapsed ? <PanelLeftOpen className="h-4 w-4" /> : <PanelLeftClose className="h-4 w-4" />}
        </button>
      </div>

      <nav className="flex-1 overflow-y-auto py-4" aria-label="Primary navigation">
        {sections.map((section) => (
          <div key={section.id} className="mb-4">
            <div className="sidebar-section-label px-4 mb-2">
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
                      'sidebar-link flex items-center gap-3 px-4 py-2 text-sm transition-fast',
                      isActive
                        ? 'active'
                        : 'text-foreground hover:bg-accent'
                    )
                  }
                >
                  <item.icon className="h-4 w-4 shrink-0" />
                  <span className="sidebar-link-label">{item.name}</span>
                </NavLink>
              ))}
          </div>
        ))}
      </nav>

      <div className="sidebar-footer px-4 py-4 border-t space-y-3">
        <div className="sidebar-user flex items-center gap-3 px-2 text-xs text-muted-foreground truncate">
          <span className="avatar-dot">{session?.user.displayName?.slice(0, 1).toUpperCase()}</span>
          <span className="sidebar-link-label truncate">{session?.user.displayName}</span>
        </div>
        <button
          type="button"
          className="sidebar-link flex w-full items-center gap-3 rounded-md px-2 py-2 text-sm text-foreground hover:bg-accent"
          onClick={signOut}
          title="Sign out"
        >
          <LogOut className="h-4 w-4" />
          <span className="sidebar-link-label">Sign out</span>
        </button>
        <div className="demo-indicator px-3 py-2 bg-muted rounded-md text-xs text-center">
          <span className="font-semibold">DEMO MODE</span>
        </div>
      </div>
    </aside>
  )
}
