export interface MockInvestigation {
  id: string
  name: string
  description: string
  status: 'active' | 'paused' | 'closed'
  priority: 'critical' | 'high' | 'medium'
  lead: string
  entityIds: string[]
  updatedAt: string
}

export const mockInvestigations: MockInvestigation[] = [
  {
    id: 'INV-001',
    name: 'Operation Nexus',
    description: 'Trace financial and logistics relationships across the primary network.',
    status: 'active',
    priority: 'critical',
    lead: 'A. Sharma',
    entityIds: ['ENT-001', 'ENT-002', 'ENT-004', 'ENT-009'],
    updatedAt: '2026-01-16T10:25:00Z',
  },
  {
    id: 'INV-002',
    name: 'Project Meridian',
    description: 'Review cross-case identities and shared communication infrastructure.',
    status: 'paused',
    priority: 'high',
    lead: 'M. Rao',
    entityIds: ['ENT-003', 'ENT-008', 'ENT-010'],
    updatedAt: '2026-01-14T15:40:00Z',
  },
]
