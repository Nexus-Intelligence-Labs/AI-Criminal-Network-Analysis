import { useState } from 'react'
import { GraphWorkspace } from '@/components/graph/GraphWorkspace'
import { EntitySheet } from '@/components/entity/EntitySheet'
import { mockGraphData } from '@/mocks/graph'
import { Entity } from '@/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Network, AlertTriangle, Users, FileText } from 'lucide-react'

export function Dashboard() {
  const [selectedEntity, setSelectedEntity] = useState<Entity | null>(null)
  const [isEntitySheetOpen, setIsEntitySheetOpen] = useState(false)

  const handleNodeClick = (entity: Entity) => {
    setSelectedEntity(entity)
    setIsEntitySheetOpen(true)
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="border-b bg-card px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Intelligence Dashboard</h1>
            <div className="flex items-center gap-2 mt-1">
              <Badge variant="outline" className="font-mono">
                CASE-2026-001
              </Badge>
              <span className="text-sm text-muted-foreground">
                Financial Network Investigation
              </span>
            </div>
          </div>
          <Button variant="outline">Change Case</Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex gap-4 p-6 overflow-hidden">
        {/* Left Sidebar Stats */}
        <div className="w-64 flex-shrink-0 space-y-4 overflow-y-auto">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Network className="h-4 w-4" />
                Network
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div>
                  <div className="text-2xl font-bold">{mockGraphData.nodes.length}</div>
                  <div className="text-xs text-muted-foreground">Entities</div>
                </div>
                <div>
                  <div className="text-2xl font-bold">{mockGraphData.edges.length}</div>
                  <div className="text-xs text-muted-foreground">Relationships</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-red-500" />
                Alerts
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Critical</span>
                  <Badge variant="destructive">3</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">High</span>
                  <Badge>4</Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Users className="h-4 w-4" />
                High Risk
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {mockGraphData.nodes.filter(n => n.isHighRisk).length}
              </div>
              <div className="text-xs text-muted-foreground">Profiles</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <FileText className="h-4 w-4" />
                Evidence
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">12</div>
              <div className="text-xs text-muted-foreground">Records</div>
            </CardContent>
          </Card>
        </div>

        {/* Graph Workspace */}
        <div className="flex-1 min-w-0">
          <GraphWorkspace
            data={mockGraphData}
            onNodeClick={handleNodeClick}
            className="h-full"
          />
        </div>
      </div>

      {/* Entity Sheet */}
      <EntitySheet
        entity={selectedEntity}
        open={isEntitySheetOpen}
        onOpenChange={setIsEntitySheetOpen}
      />
    </div>
  )
}
