export interface EntityMatchReview {
  id: string
  existing: string
  candidate: string
  confidence: number
  signals: string[]
  status: 'pending' | 'approved' | 'rejected'
}

export interface ExtractionReview {
  id: string
  kind: 'entity' | 'relationship'
  subject: string
  detail: string
  confidence: number
  source: string
  status: 'pending' | 'accepted' | 'rejected'
}

export const mockEntityMatches: EntityMatchReview[] = [
  { id: 'MATCH-001', existing: 'Raj Kumar', candidate: 'R. Kumar', confidence: 0.92, signals: ['Name similarity', 'Phone overlap', 'Organization overlap'], status: 'pending' },
  { id: 'MATCH-002', existing: 'Northstar Logistics', candidate: 'Northstar Ltd', confidence: 0.96, signals: ['Name similarity', 'Address overlap'], status: 'pending' },
]

export const mockExtractions: ExtractionReview[] = [
  { id: 'EXT-001', kind: 'entity', subject: 'Rahul Kumar', detail: 'Person', confidence: 0.91, source: 'INT-019', status: 'pending' },
  { id: 'EXT-002', kind: 'relationship', subject: 'Raj Kumar → Northstar Logistics', detail: 'works_with', confidence: 0.84, source: 'CDR-884', status: 'pending' },
]
