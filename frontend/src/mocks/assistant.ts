export interface AssistantResponse {
  text: string
  citations: string[]
}

export const mockAssistantResponses: Record<string, AssistantResponse> = {
  default: {
    text: 'The demo network contains a concentrated cluster around Raj Kumar, Northstar Logistics, and the HDFC account. Review the highlighted evidence before treating any relationship as confirmed.',
    citations: ['ENT-001', 'ENT-004', 'FIR-102'],
  },
  'Explain selected entity': {
    text: 'Raj Kumar is shown because the entity has high confidence, appears in two demo cases, and is connected to multiple relationship types including ownership and financial activity.',
    citations: ['ENT-001', 'REL-004', 'CASE-2026-001'],
  },
  'Find connected entities': {
    text: 'The closest connected entities are Sameer Rao, Northstar Logistics, the registered vehicle, and the HDFC account. The graph currently shows one hop from the selected entity.',
    citations: ['ENT-002', 'ENT-004', 'ENT-005', 'ENT-009'],
  },
  'Summarize network': {
    text: 'This demo network has a small high-confidence core, with financial and logistics relationships acting as the strongest connecting signals.',
    citations: ['REL-001', 'REL-004', 'REL-006'],
  },
  'Show supporting evidence': {
    text: 'Supporting records include FIR-102, CDR-884, and INT-019. Each record has a different confidence and review status in the evidence panel.',
    citations: ['FIR-102', 'CDR-884', 'INT-019'],
  },
}
