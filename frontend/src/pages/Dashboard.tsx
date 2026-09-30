import { useState } from 'react'
import { Link } from 'react-router-dom'
import { GraphWorkspace } from '@/components/graph/GraphWorkspace'
import { EntitySheet } from '@/components/entity/EntitySheet'
import { mockGraphData } from '@/mocks/graph'
import { Entity } from '@/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Network, AlertTriangle, Users, FileText, ArrowUpRight, Activity, Clock3 } from 'lucide-react'

export function Dashboard() {
  const [selectedEntity, setSelectedEntity] = useState<Entity | null>(null)
  const [isEntitySheetOpen, setIsEntitySheetOpen] = useState(false)

  const handleNodeClick = (entity: Entity) => {
    setSelectedEntity(entity)
    setIsEntitySheetOpen(true)
  }

  return (
    <div className="page-frame flex-1 flex flex-col overflow-hidden">
      <div className="page-header border-b bg-card px-6 py-5">
        <div>
          <p className="eyebrow">Operational overview / Demo intelligence</p>
          <h1 className="page-title">Intelligence Dashboard</h1>
          <div className="flex items-center gap-2 mt-2">
            <Badge variant="outline" className="font-mono">CASE-2026-001</Badge>
            <span className="text-sm text-muted-foreground">Financial Network Investigation</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="header-status"><span className="status-pulse" /> Live workspace</span>
          <Button variant="outline"><ArrowUpRight className="h-4 w-4" /> Export brief</Button>
        </div>
      </div>

      <div className="flex-1 overflow-auto p-6">
        <div className="metric-grid mb-6">
          <Card className="metric-card">
            <CardHeader className="pb-3">
              <CardTitle className="text-xs font-medium flex items-center justify-between">
                <span className="flex items-center gap-2"><Network className="h-4 w-4 text-cyan-400" /> Network footprint</span>
                <span className="metric-trend">+12%</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="metric-value">{mockGraphData.nodes.length}</div>
              <div className="text-xs text-muted-foreground">Entities mapped across active case</div>
            </CardContent>
          </Card>
          <Card className="metric-card">
            <CardHeader className="pb-3">
              <CardTitle className="text-xs font-medium flex items-center justify-between">
                <span className="flex items-center gap-2"><Activity className="h-4 w-4 text-violet-400" /> Relationships</span>
                <span className="metric-trend">+8%</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="metric-value">{mockGraphData.edges.length}</div>
              <div className="text-xs text-muted-foreground">Observed connections in demo dataset</div>
            </CardContent>
          </Card>
          <Card className="metric-card">
            <CardHeader className="pb-3">
              <CardTitle className="text-xs font-medium flex items-center justify-between">
                <span className="flex items-center gap-2"><AlertTriangle className="h-4 w-4 text-amber-400" /> Priority signals</span>
                <span className="metric-trend metric-trend-warning">Review</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="metric-value">07</div>
              <div className="text-xs text-muted-foreground">3 critical · 4 high severity</div>
            </CardContent>
          </Card>
          <Card className="metric-card">
            <CardHeader className="pb-3">
              <CardTitle className="text-xs font-medium flex items-center justify-between">
                <span className="flex items-center gap-2"><Clock3 className="h-4 w-4 text-emerald-400" /> Last activity</span>
                <span className="text-[10px] text-muted-foreground">2h ago</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="metric-value">12</div>
              <div className="text-xs text-muted-foreground">Evidence records reviewed</div>
            </CardContent>
          </Card>
        </div>
        <div className="mb-6 flex flex-wrap gap-2">
          <Button asChild><Link to="/investigations">Open investigation workspace</Link></Button>
          <Button asChild variant="outline"><Link to="/reviews">Review AI queue</Link></Button>
          <Button asChild variant="outline"><Link to="/saved-queries">Run saved query</Link></Button>
          <Button asChild variant="outline"><Link to="/alert-rules">Manage alert rules</Link></Button>
        </div>

        <div className="dashboard-content-grid">
          <Card className="dashboard-graph-card">
            <CardHeader className="flex flex-row items-center justify-between space-y-0">
              <div>
                <p className="eyebrow">Relationship intelligence</p>
                <CardTitle>Network overview</CardTitle>
              </div>
              <Badge variant="secondary">DEMO DATA</Badge>
            </CardHeader>
            <CardContent className="h-[520px]">
              <GraphWorkspace data={mockGraphData} onNodeClick={handleNodeClick} className="h-full" />
            </CardContent>
          </Card>

          <div className="space-y-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Users className="h-4 w-4 text-cyan-400" /> Entity risk profile
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="risk-summary"><div className="risk-ring">{mockGraphData.nodes.filter(n => n.isHighRisk).length}</div><div><div className="font-semibold">High-risk profiles</div><p className="text-xs text-muted-foreground">Require analyst review</p></div></div>
                <div className="risk-bar"><span style={{ width: '68%' }} /></div>
                <div className="flex justify-between text-[11px] text-muted-foreground"><span>Network exposure</span><strong className="text-foreground">68%</strong></div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm flex items-center gap-2"><FileText className="h-4 w-4 text-violet-400" /> Recent activity</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {['Financial records linked', 'New relationship detected', 'Entity confidence updated'].map((item, index) => (
                  <div key={item} className="activity-row"><span className="activity-dot" /><div><div className="text-sm">{item}</div><div className="text-[11px] text-muted-foreground">{index + 1}h ago · CASE-2026-001</div></div></div>
                ))}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
      <EntitySheet
        entity={selectedEntity}
        open={isEntitySheetOpen}
        onOpenChange={setIsEntitySheetOpen}
      />
    </div>
  )
}
