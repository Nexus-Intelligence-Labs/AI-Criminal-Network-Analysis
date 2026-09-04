import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { FileText } from 'lucide-react'

const mockEvidence = [
  { id: 'EVD-001', type: 'Document', case: 'CASE-2026-001', source: 'Bank Records', entities: 2, date: '2026-01-10', status: 'Verified', confidence: 0.95 },
  { id: 'EVD-002', type: 'Photo', case: 'CASE-2026-001', source: 'Surveillance', entities: 3, date: '2026-01-12', status: 'Pending', confidence: 0.88 },
  { id: 'EVD-003', type: 'Communication', case: 'CASE-2026-001', source: 'Call Records', entities: 2, date: '2026-01-14', status: 'Verified', confidence: 0.92 },
  { id: 'EVD-004', type: 'Transaction', case: 'CASE-2026-002', source: 'Financial Records', entities: 2, date: '2026-01-08', status: 'Verified', confidence: 0.96 },
]

export function Evidence() {
  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="border-b bg-card px-6 py-4">
        <h1 className="text-2xl font-bold">Evidence</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Supporting records and linked evidence
        </p>
      </div>

      <div className="flex-1 p-6 overflow-auto">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Evidence Records
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Case</TableHead>
                  <TableHead>Source</TableHead>
                  <TableHead>Entities</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Confidence</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {mockEvidence.map((evidence) => (
                  <TableRow key={evidence.id}>
                    <TableCell className="font-mono text-sm">{evidence.id}</TableCell>
                    <TableCell><Badge variant="outline">{evidence.type}</Badge></TableCell>
                    <TableCell className="font-mono text-sm">{evidence.case}</TableCell>
                    <TableCell>{evidence.source}</TableCell>
                    <TableCell>{evidence.entities}</TableCell>
                    <TableCell>{new Date(evidence.date).toLocaleDateString()}</TableCell>
                    <TableCell>
                      <Badge variant={evidence.status === 'Verified' ? 'default' : 'secondary'}>
                        {evidence.status}
                      </Badge>
                    </TableCell>
                    <TableCell>{(evidence.confidence * 100).toFixed(0)}%</TableCell>
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
