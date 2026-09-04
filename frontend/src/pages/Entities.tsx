import { useState } from 'react'
import { mockEntities } from '@/mocks/entities'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Users } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { EntityType } from '@/types'

export function Entities() {
  const navigate = useNavigate()
  const [typeFilter, setTypeFilter] = useState<EntityType | 'all'>('all')
  const [confidenceFilter, setConfidenceFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all')

  const filteredEntities = mockEntities.filter(entity => {
    const matchesType = typeFilter === 'all' || entity.type === typeFilter
    const matchesConfidence = confidenceFilter === 'all' || 
      (confidenceFilter === 'high' && entity.confidence >= 0.9) ||
      (confidenceFilter === 'medium' && entity.confidence >= 0.7 && entity.confidence < 0.9) ||
      (confidenceFilter === 'low' && entity.confidence < 0.7)
    
    return matchesType && matchesConfidence
  })

  const entityCounts = {
    all: mockEntities.length,
    person: mockEntities.filter(e => e.type === 'person').length,
    organization: mockEntities.filter(e => e.type === 'organization').length,
    vehicle: mockEntities.filter(e => e.type === 'vehicle').length,
    location: mockEntities.filter(e => e.type === 'location').length,
    phone: mockEntities.filter(e => e.type === 'phone').length,
    account: mockEntities.filter(e => e.type === 'account').length,
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="border-b bg-card px-6 py-4">
        <h1 className="text-2xl font-bold">Entities</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Browse and manage intelligence entities
        </p>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-6 overflow-auto">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Entity Index
              </CardTitle>
              <div className="flex gap-2">
                <Select value={confidenceFilter} onValueChange={(value) => setConfidenceFilter(value as typeof confidenceFilter)}>
                  <SelectTrigger className="w-40">
                    <SelectValue placeholder="Confidence" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Levels</SelectItem>
                    <SelectItem value="high">High ≥90%</SelectItem>
                    <SelectItem value="medium">Medium 70-90%</SelectItem>
                    <SelectItem value="low">Low &lt;70%</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <Tabs value={typeFilter} onValueChange={(value) => setTypeFilter(value as EntityType | 'all')}>
              <TabsList>
                <TabsTrigger value="all">All ({entityCounts.all})</TabsTrigger>
                <TabsTrigger value="person">Person ({entityCounts.person})</TabsTrigger>
                <TabsTrigger value="organization">Organization ({entityCounts.organization})</TabsTrigger>
                <TabsTrigger value="vehicle">Vehicle ({entityCounts.vehicle})</TabsTrigger>
                <TabsTrigger value="location">Location ({entityCounts.location})</TabsTrigger>
                <TabsTrigger value="phone">Phone ({entityCounts.phone})</TabsTrigger>
                <TabsTrigger value="account">Account ({entityCounts.account})</TabsTrigger>
              </TabsList>
              
              <TabsContent value={typeFilter} className="mt-4">
                {filteredEntities.length > 0 ? (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Name</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead>ID</TableHead>
                        <TableHead>Confidence</TableHead>
                        <TableHead>Cases</TableHead>
                        <TableHead>Updated</TableHead>
                        <TableHead></TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredEntities.map((entity) => (
                        <TableRow 
                          key={entity.id}
                          className="cursor-pointer hover:bg-muted/50"
                          onClick={() => navigate(`/entities/${entity.id}`)}
                        >
                          <TableCell className="font-medium">
                            <div className="flex items-center gap-2">
                              {entity.name}
                              {entity.isHighRisk && (
                                <Badge variant="destructive" className="text-xs">High Risk</Badge>
                              )}
                            </div>
                          </TableCell>
                          <TableCell>
                            <Badge variant="outline" className="capitalize">
                              {entity.type}
                            </Badge>
                          </TableCell>
                          <TableCell className="font-mono text-sm">{entity.id}</TableCell>
                          <TableCell>{(entity.confidence * 100).toFixed(0)}%</TableCell>
                          <TableCell>{entity.caseIds.length}</TableCell>
                          <TableCell className="text-sm text-muted-foreground">
                            {new Date(entity.updatedAt).toLocaleDateString()}
                          </TableCell>
                          <TableCell>
                            <Button variant="ghost" size="sm">
                              View Details
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                ) : (
                  <div className="text-center py-12">
                    <Users className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <h3 className="text-lg font-semibold mb-2">No entities found</h3>
                    <p className="text-muted-foreground">
                      No {typeFilter !== 'all' ? typeFilter : ''} entities match your filters
                    </p>
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
