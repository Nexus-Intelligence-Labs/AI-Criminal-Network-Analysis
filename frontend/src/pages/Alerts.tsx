import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { AlertCircle } from 'lucide-react'

const mockAlerts = [
  { id: '1', severity: 'critical', title: 'Unusual Network Density', description: 'High concentration of connections detected around key entity', entity: 'Raj Kumar', case: 'CASE-2026-001', time: '2 hours ago', status: 'new' },
  { id: '2', severity: 'high', title: 'Unexpected Relationship', description: 'New connection detected between previously unlinked entities', entity: 'Northstar Logistics', case: 'CASE-2026-001', time: '5 hours ago', status: 'new' },
  { id: '3', severity: 'high', title: 'High-Connectivity Entity', description: 'Entity has established 24+ connections in the network', entity: 'Raj Kumar', case: 'CASE-2026-001', time: '1 day ago', status: 'reviewing' },
  { id: '4', severity: 'medium', title: 'Communication Anomaly', description: 'Unusual call pattern detected in recent activity', entity: 'Sameer Rao', case: 'CASE-2026-001', time: '2 days ago', status: 'reviewing' },
]

export function Alerts() {
  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="border-b bg-card px-6 py-4">
        <h1 className="text-2xl font-bold">Analytical Signals</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Potential anomalies and analytical signals requiring investigation
        </p>
      </div>

      <div className="flex-1 p-6 overflow-auto">
        <div className="grid gap-4">
          {mockAlerts.map((alert) => (
            <Card key={alert.id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge variant={
                        alert.severity === 'critical' ? 'destructive' :
                        alert.severity === 'high' ? 'default' :
                        'secondary'
                      }>
                        {alert.severity}
                      </Badge>
                      <Badge variant="outline">{alert.status}</Badge>
                    </div>
                    <CardTitle className="flex items-center gap-2">
                      <AlertCircle className="h-5 w-5" />
                      {alert.title}
                    </CardTitle>
                  </div>
                  <span className="text-xs text-muted-foreground">{alert.time}</span>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground mb-4">{alert.description}</p>
                <div className="flex items-center gap-4 text-sm mb-4">
                  <span><strong>Entity:</strong> {alert.entity}</span>
                  <span className="font-mono">{alert.case}</span>
                </div>
                <div className="flex gap-2">
                  <Button size="sm">View Entity</Button>
                  <Button size="sm" variant="outline">Explore Network</Button>
                  <Button size="sm" variant="outline">Mark Reviewed</Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}
