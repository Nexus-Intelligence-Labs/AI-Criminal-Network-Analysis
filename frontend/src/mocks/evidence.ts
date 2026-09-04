export interface MockEvidenceRecord {
  id: string
  type: string
  source: string
  caseId: string
  entity: string
  relationship: string
  timestamp: string
  confidence: number
  status: 'verified' | 'pending'
}

export const mockEvidenceRecords: MockEvidenceRecord[] = [
  { id: 'FIR-102', type: 'Incident report', source: 'District records', caseId: 'CASE-2026-001', entity: 'Raj Kumar', relationship: 'knows / Northstar Logistics', timestamp: '2026-01-10T11:30:00Z', confidence: 0.95, status: 'verified' },
  { id: 'CDR-884', type: 'Communication record', source: 'Call data records', caseId: 'CASE-2026-001', entity: 'Sameer Rao', relationship: 'contacted / Raj Kumar', timestamp: '2026-01-12T08:20:00Z', confidence: 0.88, status: 'verified' },
  { id: 'INT-019', type: 'Intelligence note', source: 'Analyst intake', caseId: 'CASE-2026-002', entity: 'Northstar Logistics', relationship: 'associated_with / HDFC-XXXX-3456', timestamp: '2026-01-14T15:40:00Z', confidence: 0.81, status: 'pending' },
]
