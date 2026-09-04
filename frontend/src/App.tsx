import { Outlet } from 'react-router-dom'
import { Sidebar } from './components/layout/Sidebar'

export function DashboardShell() {
  return (
    <div className="app-shell flex h-screen bg-background text-foreground">
      <Sidebar />
      <main className="app-main flex-1 flex flex-col overflow-hidden">
        <Outlet />
      </main>
    </div>
  )
}
