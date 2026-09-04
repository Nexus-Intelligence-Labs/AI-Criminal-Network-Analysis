import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Phone, Users, CreditCard, Car, FileText, GitBranch } from 'lucide-react'

const eventTypes = {
  contact: { icon: Phone, label: 'Contact', color: 'blue' },
  meeting: { icon: Users, label: 'Meeting', color: 'green' },
  transaction: { icon: CreditCard, label: 'Transaction', color: 'purple' },
  sighting: { icon: Car, label: 'Vehicle Sighting', color: 'orange' },
  case_event: { icon: FileText, label: 'Case Event', color: 'indigo' },
  evidence: { icon: FileText, label: 'Evidence Upload', color: 'yellow' },
  discovery: { icon: GitBranch, label: 'Relationship Discovery', color: 'pink' },
}

const mockEvents = [
  { id: '1', type: 'contact', date: '2026-01-15T14:30:00Z', description: 'Phone call between Raj Kumar and Sameer Rao', entity: 'Raj Kumar', case: 'CASE-2026-001' },
  { id: '2', type: 'meeting', date: '2026-01-14T10:00:00Z', description: 'Meeting at Northstar Logistics office', entity: 'Northstar Logistics', case: 'CASE-2026-001' },
  { id: '3', type: 'transaction', date: '2026-01-13T16:45:00Z', description: 'Bank transfer ₹5,20,000', entity: 'HDFC-XXXX-3456', case: 'CASE-2026-001' },
  { id: '4', type: 'sighting', date: '2026-01-12T08:20:00Z', description: 'Vehicle spotted at Warehouse A, Gurgaon', entity: 'DL-01-AB-1234', case: 'CASE-2026-001' },
  { id: '5', type: 'case_event', date: '2026-01-11T09:00:00Z', description: 'Case status updated to Active', entity: 'System', case: 'CASE-2026-001' },
  { id: '6', type: 'evidence', date: '2026-01-10T11:30:00Z', description: 'Financial records uploaded', entity: 'Raj Kumar', case: 'CASE-2026-001' },
  { id: '7', type: 'discovery', date: '2026-01-09T15:15:00Z', description: 'New relationship detected: owns', entity: 'Raj Kumar', case: 'CASE-2026-001' },
  { id: '8', type: 'contact', date: '2026-01-08T12:00:00Z', description: 'Phone call duration 45 minutes', entity: 'Raj Kumar', case: 'CASE-2026-001' },
]

export function Timeline() {
  const [entityFilter, setEntityFilter] = useState('all')
  const [typeFilter, setTypeFilter] = useState('all')

  const filteredEvents = mockEvents.filter(event => {
    const matchesEntity = entityFilter === 'all' || event.entity === entityFilter
    const matchesType = typeFilter === 'all' || event.type === typeFilter
    return matchesEntity && matchesType
  })

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="border-b bg-card px-6 py-4">
        <h1 className="text-2xl font-bold">Timeline</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Investigation timeline and events
        </p>
      </div>

      <div className="flex-1 p-6 overflow-auto">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Investigation Events</CardTitle>
              <div className="flex gap-2">
                <Select value={entityFilter} onValueChange={setEntityFilter}>
                  <SelectTrigger className="w-48">
                    <SelectValue placeholder="Entity" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Entities</SelectItem>
                    <SelectItem value="Raj Kumar">Raj Kumar</SelectItem>
                    <SelectItem value="Northstar Logistics">Northstar Logistics</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={typeFilter} onValueChange={setTypeFilter}>
                  <SelectTrigger className="w-48">
                    <SelectValue placeholder="Event Type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Types</SelectItem>
                    {Object.entries(eventTypes).map(([key, { label }]) => (
                      <SelectItem key={key} value={key}>{label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {filteredEvents.map((event, index) => {
                const eventType = eventTypes[event.type as keyof typeof eventTypes]
                const EventIcon = eventType.icon
                const date = new Date(event.date)
                
                return (
                  <div key={event.id} className="flex gap-4">
                    <div className="flex flex-col items-center">
                      <div className="w-px h-4 bg-border" />
                      <div className="p-2 rounded-full bg-primary/10 ring-4 ring-background">
                        <EventIcon className="h-4 w-4 text-primary" />
                      </div>
                      {index < filteredEvents.length - 1 && (
                        <div className="w-px flex-1 bg-border" />
                      )}
                    </div>
                    <div className="flex-1 pb-8">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge variant="outline">{eventType.label}</Badge>
                        <span className="text-xs text-muted-foreground">
                          {date.toLocaleDateString()} {date.toLocaleTimeString()}
                        </span>
                      </div>
                      <div className="text-sm font-medium mb-1">{event.description}</div>
                      <div className="flex gap-2 text-xs text-muted-foreground">
                        <span>{event.entity}</span>
                        <span>•</span>
                        <span className="font-mono">{event.case}</span>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
