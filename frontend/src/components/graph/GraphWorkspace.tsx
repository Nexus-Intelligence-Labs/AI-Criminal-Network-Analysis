import { useEffect, useRef, useState } from 'react'
import cytoscape, { Core, NodeSingular } from 'cytoscape'
import { GraphData, Entity } from '@/types'
import { Button } from '@/components/ui/button'
import { ZoomIn, ZoomOut, Maximize2, RotateCcw } from 'lucide-react'
import { cn } from '@/lib/utils'

interface GraphWorkspaceProps {
  data: GraphData
  onNodeClick?: (entity: Entity) => void
  className?: string
}

export function GraphWorkspace({ data, onNodeClick, className }: GraphWorkspaceProps) {
  const cyRef = useRef<Core | null>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const [, setSelectedNodeId] = useState<string | null>(null)

  useEffect(() => {
    if (!containerRef.current) return

    // Initialize Cytoscape
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
        name: 'cose',
        animate: false,
        idealEdgeLength: 100,
        nodeOverlap: 20,
        refresh: 20,
        fit: true,
        padding: 30,
        randomize: false,
        componentSpacing: 100,
        nodeRepulsion: 400000,
        edgeElasticity: 100,
        nestingFactor: 5,
        gravity: 80,
        numIter: 1000,
        initialTemp: 200,
        coolingFactor: 0.95,
        minTemp: 1.0,
      },
      minZoom: 0.3,
      maxZoom: 3,
      wheelSensitivity: 0.2,
    })

    cyRef.current = cy

    // Handle node clicks
    cy.on('tap', 'node', (event) => {
      const node = event.target as NodeSingular
      const nodeId = node.id()
      const entity = node.data('entity') as Entity

      setSelectedNodeId(nodeId)

      // Highlight selected node and connected elements
      cy.elements().removeClass('dimmed highlighted')
      
      const neighborhood = node.neighborhood().add(node)
      neighborhood.addClass('highlighted')
      
      cy.elements().not(neighborhood).addClass('dimmed')

      if (onNodeClick) {
        onNodeClick(entity)
      }
    })

    // Handle background clicks
    cy.on('tap', (event) => {
      if (event.target === cy) {
        setSelectedNodeId(null)
        cy.elements().removeClass('dimmed highlighted')
      }
    })

    return () => {
      cy.destroy()
    }
  }, [data, onNodeClick])

  const handleZoomIn = () => {
    cyRef.current?.zoom(cyRef.current.zoom() * 1.2)
  }

  const handleZoomOut = () => {
    cyRef.current?.zoom(cyRef.current.zoom() * 0.8)
  }

  const handleFit = () => {
    cyRef.current?.fit(undefined, 30)
  }

  const handleReset = () => {
    setSelectedNodeId(null)
    cyRef.current?.elements().removeClass('dimmed highlighted')
    cyRef.current?.fit(undefined, 30)
  }

  return (
    <div className={cn('relative w-full h-full bg-card rounded-lg border', className)}>
      <div ref={containerRef} className="w-full h-full" />
      
      {/* Graph Controls */}
      <div className="absolute top-4 right-4 flex flex-col gap-2">
        <Button
          size="icon"
          variant="outline"
          onClick={handleZoomIn}
          className="bg-background/95 backdrop-blur"
        >
          <ZoomIn className="h-4 w-4" />
        </Button>
        <Button
          size="icon"
          variant="outline"
          onClick={handleZoomOut}
          className="bg-background/95 backdrop-blur"
        >
          <ZoomOut className="h-4 w-4" />
        </Button>
        <Button
          size="icon"
          variant="outline"
          onClick={handleFit}
          className="bg-background/95 backdrop-blur"
        >
          <Maximize2 className="h-4 w-4" />
        </Button>
        <Button
          size="icon"
          variant="outline"
          onClick={handleReset}
          className="bg-background/95 backdrop-blur"
        >
          <RotateCcw className="h-4 w-4" />
        </Button>
      </div>

      {/* Entity Count */}
      <div className="absolute bottom-4 left-4 bg-background/95 backdrop-blur px-3 py-1.5 rounded-md border text-sm">
        {data.nodes.length} entities · {data.edges.length} relationships
      </div>
    </div>
  )
}
