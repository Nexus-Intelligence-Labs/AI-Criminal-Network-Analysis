import { getApiAccessToken } from './auth/apiAuthService'
import type { GraphData, EntityType, RelationshipType } from '@/types'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export async function fetchCaseGraph(caseId: string): Promise<GraphData> {
  const token = getApiAccessToken()
  const response = await fetch(`${apiBaseUrl}/api/graph/${encodeURIComponent(caseId)}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  })
  if (!response.ok) {
    throw new Error(response.status === 401 ? 'Authentication is required to load the graph.' : 'The graph could not be loaded.')
  }
  const payload = await response.json() as {
    nodes: { id: string; type?: string; label?: string; case_id?: string }[]
    edges: { id: string; source: string; target: string; type?: string }[]
  }
  return {
    nodes: payload.nodes.map((node) => ({
      id: node.id,
      type: (node.type?.toLowerCase() as EntityType) || 'person',
      label: node.label || node.id,
      isHighRisk: false,
      confidence: 1,
      data: {
        id: node.id,
        type: (node.type?.toLowerCase() as EntityType) || 'person',
        name: node.label || node.id,
        confidence: 1,
        isHighRisk: false,
        caseIds: node.case_id ? [node.case_id] : [],
        metadata: {},
        createdAt: '',
        updatedAt: '',
      },
    })),
    edges: payload.edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      type: 'related_to' as RelationshipType,
      confidence: 1,
      data: {
        id: edge.id,
        type: 'related_to',
        sourceEntityId: edge.source,
        targetEntityId: edge.target,
        confidence: 1,
        source: 'backend',
        createdAt: '',
        metadata: { label: edge.type || 'RELATED' },
      },
    })),
  }
}
