import { useState } from 'react'
import { mockGraphData } from '@/mocks/graph'
import { Entity, EntityType } from '@/types'
import { useGraph } from '@/hooks/useGraph'
import { EntitySheet } from '@/components/entity/EntitySheet'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Input } from '@/components/ui/input'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import { Checkbox } from '@/components/ui/checkbox'
import { ConnectionExplanation } from '@/components/investigation/InvestigationPanels'
import { 
  ZoomIn, ZoomOut, Maximize2, RotateCcw, Filter, 
  Search as SearchIcon, Network as NetworkIcon, X,
  LayoutGrid, Focus
} from 'lucide-react'

const layouts = [
  { value: 'cose', label: 'Force-Directed (COSE)' },
  { value: 'breadthfirst', label: 'Breadthfirst' },
  { value: 'concentric', label: 'Concentric' },
  { value: 'circle', label: 'Circle' },
  { value: 'grid', label: 'Grid' },
]

const entityTypes: EntityType[] = ['person', 'organization', 'vehicle', 'location', 'phone', 'account']
const relationshipTypes = ['knows', 'works_with', 'owns', 'located_at', 'contacted', 'transacted_with', 'associated_with']

export function GraphPage() {
  const [selectedEntity, setSelectedEntity] = useState<Entity | null>(null)
  const [isEntitySheetOpen, setIsEntitySheetOpen] = useState(false)
  const [currentLayout, setCurrentLayout] = useState('cose')
  const [searchQuery, setSearchQuery] = useState('')
  const [showLegend, setShowLegend] = useState(true)
  const [entityTypeFilters, setEntityTypeFilters] = useState<EntityType[]>([])
  const [relationshipFilters, setRelationshipFilters] = useState<string[]>([])
  const [hopDepth, setHopDepth] = useState('1')
  const [graphMode, setGraphMode] = useState('standard')
  const [timelineMonth, setTimelineMonth] = useState(3)
  const [connectionOpen, setConnectionOpen] = useState(false)

  const handleNodeClick = (entity: Entity) => {
    setSelectedEntity(entity)
    setIsEntitySheetOpen(true)
  }

  const filteredData = {
    nodes: mockGraphData.nodes.filter(node => 
      entityTypeFilters.length === 0 || entityTypeFilters.includes(node.type)
    ),
    edges: mockGraphData.edges.filter(edge => {
      const sourceNode = mockGraphData.nodes.find(n => n.id === edge.source)
      const targetNode = mockGraphData.nodes.find(n => n.id === edge.target)
      return sourceNode && targetNode &&
        (relationshipFilters.length === 0 || relationshipFilters.includes(edge.type)) &&
        (entityTypeFilters.length === 0 || 
         (entityTypeFilters.includes(sourceNode.type) && entityTypeFilters.includes(targetNode.type)))
    }),
  }

  const {
    containerRef,
    selectedNodeId,
    zoomIn,
    zoomOut,
    fit,
    reset,
    focusNode,
    searchNodes,
    changeLayout,
  } = useGraph({
    data: filteredData,
    layout: currentLayout,
    onNodeClick: handleNodeClick,
  })

  const handleLayoutChange = (value: string) => {
    setCurrentLayout(value)
    changeLayout(value)
  }

  const handleSearch = () => {
    if (searchQuery.trim()) {
      const results = searchNodes(searchQuery)
      if (results.length > 0) {
        focusNode(results[0].id)
      }
    }
  }

  const toggleEntityFilter = (type: EntityType) => {
    setEntityTypeFilters(prev =>
      prev.includes(type)
        ? prev.filter(t => t !== type)
        : [...prev, type]
    )
  }

  const clearFilters = () => {
    setEntityTypeFilters([])
    setRelationshipFilters([])
  }

  const toggleRelationshipFilter = (type: string) => {
    setRelationshipFilters((current) => current.includes(type) ? current.filter((item) => item !== type) : [...current, type])
  }

  const handleFocusSelected = () => {
    if (selectedNodeId) {
      focusNode(selectedNodeId)
    }
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="border-b bg-card px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Network Graph</h1>
            <div className="flex items-center gap-2 mt-1">
              <Badge variant="outline" className="font-mono">CASE-2026-001</Badge>
              <span className="text-sm text-muted-foreground">
                Financial Network Investigation
              </span>
            </div>
          </div>
          <div className="flex gap-2">
            <Select value={currentLayout} onValueChange={handleLayoutChange}>
              <SelectTrigger className="w-56">
                <SelectValue placeholder="Layout" />
              </SelectTrigger>
              <SelectContent>
                {layouts.map((layout) => (
                  <SelectItem key={layout.value} value={layout.value}>
                    {layout.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* Toolbar */}
      <div className="border-b bg-card px-6 py-3">
        <div className="flex items-center gap-2">
          {/* Search */}
          <div className="flex-1 max-w-md">
            <div className="relative">
              <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search entities..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                className="pl-10"
              />
            </div>
          </div>

          {/* Filters */}
          <Popover>
            <PopoverTrigger asChild>
              <Button variant="outline" size="sm">
                <Filter className="h-4 w-4 mr-2" />
                Filters
                {entityTypeFilters.length > 0 && (
                  <Badge variant="secondary" className="ml-2">
                    {entityTypeFilters.length}
                  </Badge>
                )}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-80">
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium mb-2">Entity Types</h4>
                  <div className="space-y-2">
                    {entityTypes.map((type) => (
                      <div key={type} className="flex items-center gap-2">
                        <Checkbox
                          id={type}
                          checked={entityTypeFilters.includes(type)}
                          onCheckedChange={() => toggleEntityFilter(type)}
                        />
                        <label htmlFor={type} className="text-sm capitalize cursor-pointer">
                          {type}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="font-medium mb-2">Relationship Types</h4>
                  <div className="space-y-2">{relationshipTypes.map((type) => <div key={type} className="flex items-center gap-2"><Checkbox id={`relationship-${type}`} checked={relationshipFilters.includes(type)} onCheckedChange={() => toggleRelationshipFilter(type)} /><label htmlFor={`relationship-${type}`} className="cursor-pointer text-sm">{type.replace('_', ' ')}</label></div>)}</div>
                </div>
              </div>
            </PopoverContent>
          </Popover>

          {/* Active Filters */}
          {(entityTypeFilters.length > 0 || relationshipFilters.length > 0) && (
            <>
              {entityTypeFilters.map((type) => (
                <Badge key={type} variant="secondary" className="capitalize">
                  {type}
                  <button
                    onClick={() => toggleEntityFilter(type)}
                    className="ml-2 hover:text-destructive"
                  >
                    ×
                  </button>
                </Badge>
              ))}
              {relationshipFilters.map((type) => <Badge key={type} variant="secondary">{type.replace('_', ' ')}<button onClick={() => toggleRelationshipFilter(type)} className="ml-2 hover:text-destructive">×</button></Badge>)}
              <Button variant="ghost" size="sm" onClick={clearFilters}>
                <X className="h-4 w-4 mr-2" />
                Clear All
              </Button>
            </>
          )}

          <div className="flex-1" />

          {/* Graph Controls */}
          <Button variant="outline" size="sm" onClick={handleFocusSelected} disabled={!selectedNodeId}>
            <Focus className="h-4 w-4 mr-2" />
            Focus Selected
          </Button>
          <Select value={hopDepth} onValueChange={setHopDepth}>
            <SelectTrigger className="w-28"><SelectValue placeholder="Hops" /></SelectTrigger>
            <SelectContent>{['1', '2', '3', '4'].map((hop) => <SelectItem key={hop} value={hop}>{hop} hop{hop === '1' ? '' : 's'}</SelectItem>)}</SelectContent>
          </Select>
          <Select value={graphMode} onValueChange={setGraphMode}>
            <SelectTrigger className="w-36"><SelectValue placeholder="Mode" /></SelectTrigger>
            <SelectContent>{['standard', 'community', 'centrality', 'evidence', 'timeline'].map((mode) => <SelectItem key={mode} value={mode} className="capitalize">{mode}</SelectItem>)}</SelectContent>
          </Select>
          <Button variant="outline" size="sm" onClick={() => setConnectionOpen(true)} disabled={!selectedNodeId}>Explain connection</Button>
          <Button variant="outline" size="sm" onClick={() => setShowLegend(!showLegend)}>
            <LayoutGrid className="h-4 w-4 mr-2" />
            Legend
          </Button>
        </div>
      </div>
      <div className="graph-timebar border-b border-border bg-card px-6 py-2">
        <span className="text-xs text-muted-foreground">Temporal view</span>
        <input aria-label="Timeline month" type="range" min="1" max="9" value={timelineMonth} onChange={(event) => setTimelineMonth(Number(event.target.value))} />
        <span className="font-mono text-xs text-cyan-400">2026 / {String(timelineMonth).padStart(2, '0')}</span>
        <Badge variant="outline">Mock snapshot</Badge>
      </div>

      {/* Main Content */}
      <div className="flex-1 relative overflow-hidden">
        {/* Graph */}
        <div ref={containerRef} className="absolute inset-0 bg-card" />

        {/* Graph Controls Overlay */}
        <div className="absolute top-4 right-4 flex flex-col gap-2">
          <Button size="sm" variant="outline" onClick={zoomIn} className="bg-background/95 backdrop-blur">
            <ZoomIn className="h-4 w-4" />
          </Button>
          <Button size="sm" variant="outline" onClick={zoomOut} className="bg-background/95 backdrop-blur">
            <ZoomOut className="h-4 w-4" />
          </Button>
          <Button size="sm" variant="outline" onClick={fit} className="bg-background/95 backdrop-blur">
            <Maximize2 className="h-4 w-4" />
          </Button>
          <Button size="sm" variant="outline" onClick={reset} className="bg-background/95 backdrop-blur">
            <RotateCcw className="h-4 w-4" />
          </Button>
        </div>

        {/* Network Stats */}
        <div className="absolute bottom-4 left-4 bg-background/95 backdrop-blur px-4 py-2 rounded-md border text-sm">
          <div className="flex items-center gap-4">
            <div>
              <span className="font-medium">{filteredData.nodes.length}</span> entities
            </div>
            <div>
              <span className="font-medium">{filteredData.edges.length}</span> relationships
            </div>
            {selectedNodeId && (
              <div className="text-primary">
                <NetworkIcon className="h-4 w-4 inline mr-1" />
                Selected
              </div>
            )}
          </div>
        </div>

        {/* Legend */}
        {showLegend && (
          <Card className="absolute bottom-4 right-4 w-64 bg-background/95 backdrop-blur">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center justify-between">
                Legend
                <button onClick={() => setShowLegend(false)} className="text-muted-foreground hover:text-foreground">
                  <X className="h-4 w-4" />
                </button>
              </CardTitle>
            </CardHeader>
            <CardContent className="text-xs space-y-2">
              <div className="grid grid-cols-2 gap-2">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded-full bg-blue-500" />
                  <span>Person</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-purple-500" />
                  <span>Organization</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-green-500 rotate-45" />
                  <span>Vehicle</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-orange-500" style={{ clipPath: 'polygon(50% 0%, 100% 100%, 0% 100%)' }} />
                  <span>Location</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded-sm bg-cyan-500" />
                  <span>Phone</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-pink-500" style={{ clipPath: 'polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%)' }} />
                  <span>Account</span>
                </div>
              </div>
              <div className="pt-2 border-t space-y-1">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded-full border-2 border-red-500" />
                  <span>High Risk</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded-full border-2 border-gray-500" />
                  <span>Normal</span>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Entity Sheet */}
      <EntitySheet
        entity={selectedEntity}
        open={isEntitySheetOpen}
        onOpenChange={setIsEntitySheetOpen}
      />
      <ConnectionExplanation open={connectionOpen} onOpenChange={setConnectionOpen} />
    </div>
  )
}
