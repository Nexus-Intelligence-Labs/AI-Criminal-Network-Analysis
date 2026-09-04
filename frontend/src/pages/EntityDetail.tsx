import { useParams, useNavigate } from 'react-router-dom'
import { mockEntities } from '@/mocks/entities'
import { mockRelationships } from '@/mocks/relationships'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  User, Building2, Car, MapPin, Phone as PhoneIcon, CreditCard,
  Network, FileText, Clock, ArrowLeft
} from 'lucide-react'
import { formatDateTime } from '@/lib/utils'

const entityIcons = {
  person: User,
  organization: Building2,
  vehicle: Car,
  location: MapPin,
  phone: PhoneIcon,
  account: CreditCard,
  case: FileText,
  evidence: FileText,
  event: FileText,
}

export function EntityDetail() {
  const { entityId } = useParams()
  const navigate = useNavigate()
  
  const entity = mockEntities.find(e => e.id === entityId)
  
  if (!entity) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-2">Entity Not Found</h2>
          <p className="text-muted-foreground mb-4">The entity you're looking for doesn't exist</p>
          <Button onClick={() => navigate('/entities')}>Back to Entities</Button>
        </div>
      </div>
    )
  }

  const Icon = entityIcons[entity.type]
  const entityRelationships = mockRelationships.filter(
    r => r.sourceEntityId === entity.id || r.targetEntityId === entity.id
  )

  const connectedEntities = entityRelationships.map(rel => {
    const otherId = rel.sourceEntityId === entity.id ? rel.targetEntityId : rel.sourceEntityId
    return mockEntities.find(e => e.id === otherId)
  }).filter(Boolean)

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="border-b bg-card px-6 py-4">
        <Button variant="ghost" size="sm" onClick={() => navigate('/entities')} className="mb-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Entities
        </Button>
        <div className="flex items-start gap-4">
          <div className="p-3 rounded-lg bg-primary/10">
            <Icon className="h-8 w-8 text-primary" />
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <h1 className="text-3xl font-bold">{entity.name}</h1>
              {entity.isHighRisk && (
                <Badge variant="destructive">High Risk</Badge>
              )}
            </div>
            <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
              <span className="capitalize">{entity.type}</span>
              <span>•</span>
              <span className="font-mono">{entity.id}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-6 overflow-auto">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Column */}
          <div className="lg:col-span-2 space-y-6">
            {/* Identity */}
            <Card>
              <CardHeader>
                <CardTitle>Identity</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="text-sm text-muted-foreground mb-1">Primary ID</div>
                  <div className="font-mono">{entity.id}</div>
                </div>
                {entity.aliases && entity.aliases.length > 0 && (
                  <div>
                    <div className="text-sm text-muted-foreground mb-2">Aliases</div>
                    <div className="flex flex-wrap gap-2">
                      {entity.aliases.map((alias, i) => (
                        <Badge key={i} variant="secondary">{alias}</Badge>
                      ))}
                    </div>
                  </div>
                )}
                {Object.keys(entity.metadata).length > 0 && (
                  <div>
                    <div className="text-sm text-muted-foreground mb-2">Additional Information</div>
                    <div className="grid grid-cols-2 gap-4">
                      {Object.entries(entity.metadata).map(([key, value]) => (
                        <div key={key}>
                          <div className="text-sm text-muted-foreground capitalize">
                            {key.replace('_', ' ')}
                          </div>
                          <div className="font-medium">{String(value)}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Relationships */}
            <Card>
              <CardHeader>
                <CardTitle>Relationships</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="mb-4">
                  <div className="text-2xl font-bold">{entityRelationships.length}</div>
                  <div className="text-sm text-muted-foreground">Connected Entities</div>
                </div>
                {connectedEntities.length > 0 && (
                  <div className="space-y-2">
                    {connectedEntities.slice(0, 5).map((connected) => (
                      <div
                        key={connected!.id}
                        className="flex items-center justify-between p-3 rounded-md border bg-card hover:bg-accent transition-fast cursor-pointer"
                        onClick={() => navigate(`/entities/${connected!.id}`)}
                      >
                        <div className="flex items-center gap-3">
                          <Badge variant="outline" className="capitalize">
                            {connected!.type}
                          </Badge>
                          <span className="font-medium">{connected!.name}</span>
                        </div>
                        <Button variant="ghost" size="sm">View</Button>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Processing */}
            <Card>
              <CardHeader>
                <CardTitle>Processing</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="text-sm text-muted-foreground mb-2">Confidence</div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-primary"
                        style={{ width: `${entity.confidence * 100}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium">{(entity.confidence * 100).toFixed(0)}%</span>
                  </div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground mb-1">Resolution Status</div>
                  <Badge>Resolved</Badge>
                </div>
              </CardContent>
            </Card>

            {/* Cases */}
            <Card>
              <CardHeader>
                <CardTitle>Related Cases</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {entity.caseIds.map((caseId) => (
                    <div
                      key={caseId}
                      className="p-3 rounded-md border bg-card hover:bg-accent transition-fast cursor-pointer"
                      onClick={() => navigate(`/cases/${caseId}`)}
                    >
                      <div className="font-mono text-sm">{caseId}</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Timeline */}
            <Card>
              <CardHeader>
                <CardTitle>Timeline</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <div className="text-sm text-muted-foreground mb-1">Created</div>
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">{formatDateTime(entity.createdAt)}</span>
                  </div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground mb-1">Last Updated</div>
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">{formatDateTime(entity.updatedAt)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button className="w-full" onClick={() => navigate('/graph')}>
                  <Network className="h-4 w-4 mr-2" />
                  Explore Network
                </Button>
                <Button className="w-full" variant="outline" onClick={() => navigate('/evidence')}>
                  <FileText className="h-4 w-4 mr-2" />
                  View Evidence
                </Button>
                <Button className="w-full" variant="outline" onClick={() => navigate('/timeline')}>
                  <Clock className="h-4 w-4 mr-2" />
                  View Timeline
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
