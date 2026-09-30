import { useState } from 'react'
import { mockEntities } from '@/mocks/entities'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
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
import { Search as SearchIcon, Filter, X } from 'lucide-react'
import { ChevronDown, Sparkles } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { EntityType } from '@/types'

export function Search() {
  const navigate = useNavigate()
  const [searchQuery, setSearchQuery] = useState('')
  const [typeFilter, setTypeFilter] = useState<EntityType | 'all'>('all')
  const [confidenceFilter, setConfidenceFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all')
  const [showBuilder, setShowBuilder] = useState(false)
  const [hopDepth, setHopDepth] = useState('3')
  const [relationshipFilter, setRelationshipFilter] = useState('any')

  const filteredEntities = mockEntities.filter(entity => {
    const matchesSearch = entity.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         entity.id.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesType = typeFilter === 'all' || entity.type === typeFilter
    const matchesConfidence = confidenceFilter === 'all' || 
      (confidenceFilter === 'high' && entity.confidence >= 0.9) ||
      (confidenceFilter === 'medium' && entity.confidence >= 0.7 && entity.confidence < 0.9) ||
      (confidenceFilter === 'low' && entity.confidence < 0.7)
    
    return matchesSearch && matchesType && matchesConfidence
  })

  const clearFilters = () => {
    setSearchQuery('')
    setTypeFilter('all')
    setConfidenceFilter('all')
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="border-b bg-card px-6 py-4">
        <h1 className="text-2xl font-bold">Search</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Search across entities, cases, and evidence
        </p>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-6 overflow-auto">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">Entity Search <Button variant="outline" size="sm" onClick={() => setShowBuilder((value) => !value)}><Sparkles className="mr-2 h-4 w-4 text-cyan-400" />Query builder <ChevronDown className="ml-1 h-3 w-3" /></Button></CardTitle>
          </CardHeader>
          <CardContent>
            {/* Search & Filters */}
            <div className="space-y-4 mb-6">
              {showBuilder && <div className="query-builder"><div><span className="query-label">Find</span><Select value={typeFilter} onValueChange={(value) => setTypeFilter(value as EntityType | 'all')}><SelectTrigger><SelectValue placeholder="People" /></SelectTrigger><SelectContent><SelectItem value="all">Any entity</SelectItem><SelectItem value="person">People</SelectItem><SelectItem value="organization">Organizations</SelectItem><SelectItem value="vehicle">Vehicles</SelectItem></SelectContent></Select></div><span className="query-label">connected to</span><Input placeholder="Organization X" /><span className="query-label">within</span><select className="input h-9" value={hopDepth} onChange={(event) => setHopDepth(event.target.value)}><option value="1">1 hop</option><option value="2">2 hops</option><option value="3">3 hops</option><option value="4">4 hops</option></select><span className="query-label">with</span><select className="input h-9" value={relationshipFilter} onChange={(event) => setRelationshipFilter(event.target.value)}><option value="any">Any relationship</option><option value="knows">Knows</option><option value="owns">Owns</option><option value="contacted">Contacted</option></select><Button onClick={() => setShowBuilder(false)}>Run investigation</Button></div>}
              <div className="flex gap-4">
                <div className="flex-1 relative">
                  <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search by name or ID..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <Select value={typeFilter} onValueChange={(value) => setTypeFilter(value as EntityType | 'all')}>
                  <SelectTrigger className="w-48">
                    <SelectValue placeholder="Entity Type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Types</SelectItem>
                    <SelectItem value="person">Person</SelectItem>
                    <SelectItem value="organization">Organization</SelectItem>
                    <SelectItem value="vehicle">Vehicle</SelectItem>
                    <SelectItem value="location">Location</SelectItem>
                    <SelectItem value="phone">Phone</SelectItem>
                    <SelectItem value="account">Account</SelectItem>
                  </SelectContent>
                </Select>
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
                {(typeFilter !== 'all' || confidenceFilter !== 'all' || searchQuery) && (
                  <Button variant="outline" onClick={clearFilters}>
                    <X className="h-4 w-4 mr-2" />
                    Clear
                  </Button>
                )}
              </div>

              {/* Active Filters */}
              {(typeFilter !== 'all' || confidenceFilter !== 'all') && (
                <div className="flex gap-2 items-center">
                  <Filter className="h-4 w-4 text-muted-foreground" />
                  {typeFilter !== 'all' && (
                    <Badge variant="secondary">
                      {typeFilter}
                      <button onClick={() => setTypeFilter('all')} className="ml-2">×</button>
                    </Badge>
                  )}
                  {confidenceFilter !== 'all' && (
                    <Badge variant="secondary">
                      {confidenceFilter} confidence
                      <button onClick={() => setConfidenceFilter('all')} className="ml-2">×</button>
                    </Badge>
                  )}
                </div>
              )}
            </div>

            {/* Results Count */}
            <div className="mb-4 text-sm text-muted-foreground">
              {filteredEntities.length} {filteredEntities.length === 1 ? 'result' : 'results'}
            </div>

            {/* Results Table */}
            {filteredEntities.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Entity</TableHead>
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
                    <TableRow key={entity.id} className="cursor-pointer hover:bg-muted/50">
                      <TableCell className="font-medium">{entity.name}</TableCell>
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
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => navigate(`/entities/${entity.id}`)}
                        >
                          View Details
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <div className="text-center py-12">
                <SearchIcon className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No entities found</h3>
                <p className="text-muted-foreground">
                  Try adjusting your search or filters
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
