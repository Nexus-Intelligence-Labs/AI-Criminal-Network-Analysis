import { GraphData, GraphNode, GraphEdge } from '@/types'
import { mockEntities } from './entities'
import { mockRelationships } from './relationships'

// Build graph data from entities and relationships for CASE-2026-001
const case001EntityIds = ['ENT-001', 'ENT-002', 'ENT-003', 'ENT-004', 'ENT-005', 'ENT-006', 'ENT-007', 'ENT-009']

export const mockGraphData: GraphData = {
  nodes: mockEntities
    .filter(e => case001EntityIds.includes(e.id))
    .map((entity): GraphNode => ({
      id: entity.id,
      type: entity.type,
      label: entity.name,
      isHighRisk: entity.isHighRisk,
      confidence: entity.confidence,
      data: entity,
    })),
  edges: mockRelationships
    .filter(r =>
      case001EntityIds.includes(r.sourceEntityId) &&
      case001EntityIds.includes(r.targetEntityId)
    )
    .map((relationship): GraphEdge => ({
      id: relationship.id,
      source: relationship.sourceEntityId,
      target: relationship.targetEntityId,
      type: relationship.type,
      confidence: relationship.confidence,
      data: relationship,
    })),
}
