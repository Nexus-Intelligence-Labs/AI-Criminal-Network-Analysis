import { mockCases } from '@/mocks/cases'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { formatDate } from '@/lib/utils'

const statusColors = {
  active: 'default',
  pending: 'secondary',
  closed: 'outline',
  archived: 'outline',
} as const

const priorityColors = {
  critical: 'destructive',
  high: 'default',
  medium: 'secondary',
  low: 'outline',
} as const

export function Cases() {
  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="border-b bg-card px-6 py-4">
        <h1 className="text-2xl font-bold">Cases</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Manage and review investigation cases
        </p>
      </div>

      <div className="flex-1 p-6 overflow-auto">
        <Card>
          <CardHeader>
            <CardTitle>All Cases</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Case ID</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Priority</TableHead>
                  <TableHead>Entities</TableHead>
                  <TableHead>Alerts</TableHead>
                  <TableHead>Updated</TableHead>
                  <TableHead></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {mockCases.map((caseItem) => (
                  <TableRow key={caseItem.id}>
                    <TableCell className="font-mono text-sm">
                      {caseItem.id}
                    </TableCell>
                    <TableCell className="font-medium">
                      {caseItem.name}
                    </TableCell>
                    <TableCell>
                      <Badge variant={statusColors[caseItem.status]}>
                        {caseItem.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={priorityColors[caseItem.priority]}>
                        {caseItem.priority}
                      </Badge>
                    </TableCell>
                    <TableCell>{caseItem.entityCount}</TableCell>
                    <TableCell>{caseItem.alertCount}</TableCell>
                    <TableCell>{formatDate(caseItem.updatedAt)}</TableCell>
                    <TableCell>
                      <Button variant="ghost" size="sm">
                        View
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
