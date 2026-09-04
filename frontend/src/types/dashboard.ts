// Entity Types
export type EntityType = 
  | 'person' 
  | 'organization' 
  | 'vehicle' 
  | 'location' 
  | 'phone' 
  | 'account' 
  | 'case' 
  | 'evidence'
  | 'event'

export interface Entity {
  id: string
  type: EntityType
  name: string
  aliases?: string[]
  confidence: number
  isHighRisk: boolean
  caseIds: string[]
  metadata: Record<string, unknown>
  createdAt: string
  updatedAt: string
}

// Relationship Types
export type RelationshipType =
  | 'knows'
  | 'works_with'
  | 'owns'
  | 'located_at'
  | 'contacted'
  | 'transacted_with'
  | 'associated_with'
  | 'related_to'

export interface Relationship {
  id: string
  type: RelationshipType
  sourceEntityId: string
  targetEntityId: string
  confidence: number
  source: string
  metadata: Record<string, unknown>
  createdAt: string
}

// Case Types
export type CaseStatus = 'active' | 'pending' | 'closed' | 'archived'
export type CasePriority = 'critical' | 'high' | 'medium' | 'low'

export interface Case {
  id: string
  name: string
  status: CaseStatus
  priority: CasePriority
  leadEntityId?: string
  entityCount: number
  alertCount: number
  createdAt: string
  updatedAt: string
}

// Evidence Types
export type EvidenceType = 
  | 'document'
  | 'photo'
  | 'video'
  | 'audio'
  | 'communication'
  | 'transaction'
  | 'record'

export type EvidenceStatus = 'pending' | 'verified' | 'rejected'

export interface Evidence {
  id: string
  type: EvidenceType
  caseId: string
  source: string
  linkedEntityIds: string[]
  status: EvidenceStatus
  confidence: number
  date: string
  createdAt: string
}

// Timeline Event Types
export type TimelineEventType =
  | 'contact'
  | 'meeting'
  | 'transaction'
  | 'sighting'
  | 'case_event'
  | 'evidence_upload'
  | 'relationship_discovered'

export interface TimelineEvent {
  id: string
  type: TimelineEventType
  title: string
  description: string
  entityIds: string[]
  caseId?: string
  evidenceId?: string
  timestamp: string
}

// Alert Types
export type AlertSeverity = 'critical' | 'high' | 'medium' | 'low'
export type AlertStatus = 'new' | 'reviewing' | 'resolved' | 'dismissed'

export interface Alert {
  id: string
  severity: AlertSeverity
  title: string
  description: string
  caseId?: string
  entityIds: string[]
  status: AlertStatus
  timestamp: string
}

// Graph Types
export interface GraphNode {
  id: string
  type: EntityType
  label: string
  isHighRisk: boolean
  confidence: number
  data: Entity
}

export interface GraphEdge {
  id: string
  source: string
  target: string
  type: RelationshipType
  confidence: number
  data: Relationship
}

export interface GraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

// Analytics Types
export interface AnalyticsMetric {
  label: string
  value: number
  change?: number
}

export interface ChartDataPoint {
  name: string
  value: number
  [key: string]: string | number
}
