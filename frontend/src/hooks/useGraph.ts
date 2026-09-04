import { useEffect, useRef, useState } from 'react'
import cytoscape, { Core, NodeSingular, EdgeSingular, type LayoutOptions } from 'cytoscape'
import { GraphData, Entity } from '@/types'

export interface UseGraphOptions {
  data: GraphData
  layout?: string
  onNodeClick?: (entity: Entity) => void
  onEdgeClick?: (edge: EdgeSingular) => void
}

export function useGraph({ data, layout = 'cose', onNodeClick, onEdgeClick }: UseGraphOptions) {
  const cyRef = useRef<Core | null>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null)

  useEffect(() => {
    if (!containerRef.current) return

    const cy = cytoscape({
      container: containerRef.current,
      elements: {
        nodes: data.nodes.map(node => ({
          data: {
            id: node.id,
            label: node.label,
            type: node.type,
            isHighRisk: node.isHighRisk,
            confidence: node.confidence,
            entity: node.data,
          },
        })),
        edges: data.edges.map(edge => ({
          data: {
            id: edge.id,
            source: edge.source,
            target: edge.target,
            type: edge.type,
            confidence: edge.confidence,
          },
        })),
      },
      style: [
        {
          selector: 'node',
          style: {
            'background-color': '#374151',
            'border-color': '#6b7280',
            'border-width': 2,
            label: 'data(label)',
            'text-valign': 'bottom',
            'text-halign': 'center',
            'text-margin-y': 5,
            color: '#e5e7eb',
            'font-size': '11px',
            width: 40,
            height: 40,
            'text-wrap': 'wrap',
            'text-max-width': '80px',
          },
        },
        {
          selector: 'node[type="person"]',
          style: {
            shape: 'ellipse',
            'background-color': '#3b82f6',
          },
        },
        {
          selector: 'node[type="organization"]',
          style: {
            shape: 'rectangle',
            'background-color': '#8b5cf6',
          },
        },
        {
          selector: 'node[type="vehicle"]',
          style: {
            shape: 'diamond',
            'background-color': '#10b981',
          },
        },
        {
          selector: 'node[type="location"]',
          style: {
            shape: 'triangle',
            'background-color': '#f59e0b',
          },
        },
        {
          selector: 'node[type="phone"]',
          style: {
            shape: 'round-rectangle',
            'background-color': '#06b6d4',
          },
        },
        {
          selector: 'node[type="account"]',
          style: {
            shape: 'round-hexagon',
            'background-color': '#ec4899',
          },
        },
        {
          selector: 'node[isHighRisk]',
          style: {
            'border-color': '#ef4444',
            'border-width': 3,
          },
        },
        {
          selector: 'node:selected',
          style: {
            'border-width': 4,
            'border-color': '#60a5fa',
          },
        },
        {
          selector: 'edge',
          style: {
            width: 2,
            'line-color': '#4b5563',
            'target-arrow-color': '#4b5563',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
          },
        },
        {
          selector: 'edge:selected',
          style: {
            'line-color': '#60a5fa',
            'target-arrow-color': '#60a5fa',
            width: 3,
          },
        },
        {
          selector: '.dimmed',
          style: {
            opacity: 0.3,
          },
        },
        {
          selector: '.highlighted',
          style: {
            opacity: 1,
          },
        },
      ],
      layout: {
        name: layout,
        fit: true,
        padding: 30,
      } as LayoutOptions,
      minZoom: 0.3,
      maxZoom: 3,
      wheelSensitivity: 0.2,
    })

    cyRef.current = cy

    // Node click handler
    cy.on('tap', 'node', (event) => {
      const node = event.target as NodeSingular
      const nodeId = node.id()
      const entity = node.data('entity') as Entity

      setSelectedNodeId(nodeId)

      // Highlight selected node and neighbors
      cy.elements().removeClass('dimmed highlighted')
      const neighborhood = node.neighborhood().add(node)
      neighborhood.addClass('highlighted')
      cy.elements().not(neighborhood).addClass('dimmed')

      if (onNodeClick) {
        onNodeClick(entity)
      }
    })

    // Edge click handler
    cy.on('tap', 'edge', (event) => {
      const edge = event.target as EdgeSingular
      if (onEdgeClick) {
        onEdgeClick(edge)
      }
    })

    // Background click handler
    cy.on('tap', (event) => {
      if (event.target === cy) {
        setSelectedNodeId(null)
        cy.elements().removeClass('dimmed highlighted')
      }
    })

    return () => {
      cy.destroy()
    }
  }, [data, layout, onNodeClick, onEdgeClick])

  const zoomIn = () => {
    cyRef.current?.zoom(cyRef.current.zoom() * 1.2)
  }

  const zoomOut = () => {
    cyRef.current?.zoom(cyRef.current.zoom() * 0.8)
  }

  const fit = () => {
    cyRef.current?.fit(undefined, 30)
  }

  const reset = () => {
    setSelectedNodeId(null)
    cyRef.current?.elements().removeClass('dimmed highlighted')
    cyRef.current?.fit(undefined, 30)
  }

  const focusNode = (nodeId: string) => {
    const node = cyRef.current?.$id(nodeId)
    if (node) {
      node.select()
      cyRef.current?.animate({
        center: { eles: node },
        zoom: 1.5,
      }, {
        duration: 200,
      })
    }
  }

  const searchNodes = (query: string) => {
    if (!cyRef.current) return []
    const lowerQuery = query.toLowerCase()
    return cyRef.current.nodes().filter((node: NodeSingular) => {
      const label = node.data('label')?.toLowerCase() || ''
      return label.includes(lowerQuery)
    }).map((node: NodeSingular) => ({
      id: node.id(),
      label: node.data('label'),
      type: node.data('type'),
    }))
  }

  const changeLayout = (layoutName: string) => {
    cyRef.current?.layout({
      name: layoutName,
      fit: true,
      padding: 30,
    } as LayoutOptions).run()
  }

  return {
    containerRef,
    cyRef,
    selectedNodeId,
    zoomIn,
    zoomOut,
    fit,
    reset,
    focusNode,
    searchNodes,
    changeLayout,
  }
}
