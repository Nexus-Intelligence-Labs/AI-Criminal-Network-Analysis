import { useState } from 'react'
import { Activity, Bot, FilePlus2, Network, Plus, Search, Sparkles } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { GraphWorkspace } from '@/components/graph/GraphWorkspace'
import { AssistantPanel, ConnectionExplanation, CrossCasePanel, EvidencePanel, NotesPanel, WhyThisObject } from '@/components/investigation/InvestigationPanels'
import { mockGraphData } from '@/mocks/graph'
import { mockInvestigations } from '@/mocks/investigations'
import { mockEntities } from '@/mocks/entities'
import type { Entity } from '@/types'

export function Investigations() {
  const [activeInvestigation, setActiveInvestigation] = useState(mockInvestigations[0])
  const [selectedEntity, setSelectedEntity] = useState<Entity>(mockEntities[0])
  const [query, setQuery] = useState('')
  const [evidenceOpen, setEvidenceOpen] = useState(false)
  const [assistantOpen, setAssistantOpen] = useState(false)
  const [connectionOpen, setConnectionOpen] = useState(false)
  const filteredEntities = mockEntities.filter((entity) => entity.name.toLowerCase().includes(query.toLowerCase()))

  return (
    <div className="page-frame flex-1 flex flex-col overflow-hidden">
      <div className="page-header border-b bg-card px-6 py-5"><div><p className="eyebrow">Investigation workspace / Demo mode</p><h1 className="page-title">{activeInvestigation.name}</h1><p className="mt-2 text-sm text-muted-foreground">{activeInvestigation.description}</p></div><div className="flex gap-2"><Button variant="outline"><FilePlus2 className="h-4 w-4" /> New investigation</Button><Button onClick={() => setAssistantOpen(true)}><Bot className="h-4 w-4" /> Ask assistant</Button></div></div>
      <div className="investigation-workspace flex-1 overflow-hidden">
        <aside className="investigation-nav overflow-y-auto border-r border-border p-4">
          <div className="mb-4 flex items-center justify-between"><p className="eyebrow mb-0">Saved investigations</p><Button size="icon" variant="ghost" aria-label="Create investigation"><Plus className="h-4 w-4" /></Button></div>
          <div className="space-y-2">{mockInvestigations.map((investigation) => <button type="button" key={investigation.id} onClick={() => setActiveInvestigation(investigation)} className={`investigation-list-item ${activeInvestigation.id === investigation.id ? 'selected' : ''}`}><div className="flex items-center justify-between"><span className="font-medium">{investigation.name}</span><Badge variant={investigation.priority === 'critical' ? 'destructive' : 'secondary'}>{investigation.priority}</Badge></div><span className="text-xs text-muted-foreground">{investigation.lead} · {investigation.status}</span></button>)}</div>
          <div className="mt-8"><p className="eyebrow">Workspace actions</p><div className="space-y-2"><Button className="w-full justify-start" variant="outline"><Plus className="h-4 w-4" /> Add entity</Button><Button className="w-full justify-start" variant="outline" onClick={() => setEvidenceOpen(true)}><FilePlus2 className="h-4 w-4" /> Add evidence</Button><Button className="w-full justify-start" variant="outline"><Activity className="h-4 w-4" /> Generate summary</Button></div></div>
        </aside>
        <main className="investigation-main overflow-y-auto p-4 lg:p-6">
          <div className="mb-4 flex flex-wrap items-center gap-2"><Badge variant="outline">{activeInvestigation.status}</Badge><Badge variant="secondary">Lead: {activeInvestigation.lead}</Badge><span className="text-xs text-muted-foreground">Updated Jan 16, 2026 · Local demo state</span></div>
          <Tabs defaultValue="network">
            <TabsList><TabsTrigger value="network"><Network className="mr-2 h-4 w-4" />Network</TabsTrigger><TabsTrigger value="entities"><Search className="mr-2 h-4 w-4" />Entities</TabsTrigger><TabsTrigger value="evidence"><FilePlus2 className="mr-2 h-4 w-4" />Evidence</TabsTrigger><TabsTrigger value="comparison"><Activity className="mr-2 h-4 w-4" />Cross-case</TabsTrigger></TabsList>
            <TabsContent value="network" className="space-y-4">
              <Card><CardHeader className="flex flex-row items-center justify-between space-y-0"><div><p className="eyebrow">Primary analysis</p><CardTitle>Network investigation</CardTitle></div><div className="flex gap-2"><Button size="sm" variant="outline" onClick={() => setConnectionOpen(true)}>Explain connection</Button><Button size="sm" variant="outline" onClick={() => setAssistantOpen(true)}><Sparkles className="h-4 w-4" /> Ask about graph</Button></div></CardHeader><CardContent className="h-[480px]"><GraphWorkspace data={mockGraphData} onNodeClick={setSelectedEntity} className="h-full" /></CardContent></Card>
              <div className="grid gap-4 lg:grid-cols-2"><NotesPanel /><WhyThisObject entity={selectedEntity} /></div>
            </TabsContent>
            <TabsContent value="entities"><Card><CardHeader><CardTitle>Entities in investigation</CardTitle></CardHeader><CardContent><Input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Filter entities..." /><div className="mt-4 grid gap-2 md:grid-cols-2">{filteredEntities.map((entity) => <button type="button" key={entity.id} className="entity-select-card" onClick={() => setSelectedEntity(entity)}><div><strong>{entity.name}</strong><p className="text-xs text-muted-foreground">{entity.id} · {entity.type}</p></div><Badge variant={entity.isHighRisk ? 'destructive' : 'outline'}>{entity.isHighRisk ? 'High risk' : `${Math.round(entity.confidence * 100)}%`}</Badge></button>)}</div></CardContent></Card></TabsContent>
            <TabsContent value="evidence"><Card><CardHeader><CardTitle>Evidence traceability</CardTitle></CardHeader><CardContent><p className="mb-4 text-sm text-muted-foreground">Review source records and the extraction-to-graph provenance chain.</p><Button onClick={() => setEvidenceOpen(true)}>Open evidence panel</Button></CardContent></Card></TabsContent>
            <TabsContent value="comparison"><CrossCasePanel /></TabsContent>
          </Tabs>
        </main>
        <aside className="investigation-inspector hidden overflow-y-auto border-l border-border p-4 xl:block"><p className="eyebrow">Context inspector</p><Card><CardHeader><CardTitle className="text-base">{selectedEntity.name}</CardTitle><p className="text-xs capitalize text-muted-foreground">{selectedEntity.type} · {selectedEntity.id}</p></CardHeader><CardContent className="space-y-3"><Badge variant={selectedEntity.isHighRisk ? 'destructive' : 'outline'}>{selectedEntity.isHighRisk ? 'High risk' : 'Monitored'}</Badge><p className="text-sm text-muted-foreground">Confidence {Math.round(selectedEntity.confidence * 100)}% across the demo evidence set.</p><Button className="w-full" variant="outline" onClick={() => setEvidenceOpen(true)}>View evidence</Button><Button className="w-full" variant="outline" onClick={() => setConnectionOpen(true)}>Explain connection</Button></CardContent></Card></aside>
      </div>
      <EvidencePanel open={evidenceOpen} onOpenChange={setEvidenceOpen} /><AssistantPanel open={assistantOpen} onOpenChange={setAssistantOpen} /><ConnectionExplanation open={connectionOpen} onOpenChange={setConnectionOpen} />
    </div>
  )
}
