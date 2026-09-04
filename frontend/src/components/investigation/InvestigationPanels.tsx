import { useState } from 'react'
import { AlertCircle, Bot, Check, ChevronRight, FileSearch, Info, Send, Sparkles, StickyNote, X } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Separator } from '@/components/ui/separator'
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import { mockAssistantResponses } from '@/mocks/assistant'
import { mockEvidenceRecords } from '@/mocks/evidence'
import { mockEntities } from '@/mocks/entities'
import { mockRelationships } from '@/mocks/relationships'
import type { Entity } from '@/types'

export function EvidencePanel({ open, onOpenChange }: { open: boolean; onOpenChange: (open: boolean) => void }) {
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="w-full overflow-y-auto sm:max-w-lg">
        <SheetHeader>
          <p className="eyebrow">Traceability / Demo records</p>
          <SheetTitle>Evidence and provenance</SheetTitle>
        </SheetHeader>
        <div className="mt-6 space-y-5">
          {mockEvidenceRecords.map((record) => (
            <Card key={record.id}>
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between gap-3">
                  <div><CardTitle className="text-sm">{record.id}</CardTitle><p className="text-xs text-muted-foreground">{record.type}</p></div>
                  <Badge variant={record.status === 'verified' ? 'default' : 'secondary'}>{record.status}</Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <div className="grid grid-cols-2 gap-3 text-xs"><span className="text-muted-foreground">Source<br /><strong className="text-foreground">{record.source}</strong></span><span className="text-muted-foreground">Case<br /><strong className="text-foreground font-mono">{record.caseId}</strong></span><span className="text-muted-foreground">Entity<br /><strong className="text-foreground">{record.entity}</strong></span><span className="text-muted-foreground">Confidence<br /><strong className="text-foreground">{Math.round(record.confidence * 100)}%</strong></span></div>
                <Separator />
                <p className="text-xs"><span className="text-muted-foreground">Relationship:</span> {record.relationship}</p>
                <div className="provenance-trail"><span>Source record</span><ChevronRight /><span>Extraction</span><ChevronRight /><span>Resolution</span><ChevronRight /><span>Graph</span></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </SheetContent>
    </Sheet>
  )
}

export function ConnectionExplanation({ open, onOpenChange }: { open: boolean; onOpenChange: (open: boolean) => void }) {
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="w-full overflow-y-auto sm:max-w-lg">
        <SheetHeader><p className="eyebrow">Analysis / Demo result</p><SheetTitle>Explain this connection</SheetTitle></SheetHeader>
        <div className="mt-6 space-y-5">
          <div className="connection-summary"><div><span className="text-xs text-muted-foreground">Source</span><strong>Raj Kumar</strong></div><span className="connection-arrow">→</span><div><span className="text-xs text-muted-foreground">Target</span><strong>Northstar Logistics</strong></div></div>
          <Card><CardHeader><CardTitle className="text-sm">Connection summary</CardTitle></CardHeader><CardContent className="grid grid-cols-2 gap-4 text-sm"><div><span className="text-xs text-muted-foreground">Path type</span><p>Indirect</p></div><div><span className="text-xs text-muted-foreground">Path length</span><p>2 hops</p></div><div><span className="text-xs text-muted-foreground">Confidence</span><p className="text-emerald-400">91%</p></div><div><span className="text-xs text-muted-foreground">First observed</span><p>Dec 10, 2025</p></div></CardContent></Card>
          <div className="path-sequence"><div>Raj Kumar</div><span>knows</span><div>Sameer Rao</div><span>works_with</span><div>Northstar Logistics</div></div>
          <div><h3 className="mb-2 text-sm font-semibold">Supporting evidence</h3><div className="space-y-2">{['FIR-102', 'CDR-884'].map((id) => <div key={id} className="flex items-center justify-between rounded-lg border border-border p-3 text-sm"><span className="flex items-center gap-2"><FileSearch className="h-4 w-4 text-cyan-400" />{id}</span><Badge variant="outline">View</Badge></div>)}</div></div>
          <Button className="w-full" onClick={() => onOpenChange(false)}>Add explanation to notes</Button>
        </div>
      </SheetContent>
    </Sheet>
  )
}

export function AssistantPanel({ open, onOpenChange }: { open: boolean; onOpenChange: (open: boolean) => void }) {
  const [messages, setMessages] = useState([{ role: 'assistant', text: mockAssistantResponses.default.text, citations: mockAssistantResponses.default.citations }])
  const [prompt, setPrompt] = useState('')
  const send = (value = prompt) => {
    const key = value || 'default'
    const response = mockAssistantResponses[key] ?? mockAssistantResponses.default
    setMessages((current) => [...current, { role: 'user', text: value, citations: [] }, { role: 'assistant', text: response.text, citations: response.citations }])
    setPrompt('')
  }
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="assistant-sheet flex w-full flex-col sm:max-w-md">
        <SheetHeader><p className="eyebrow flex items-center gap-2"><Sparkles className="h-3 w-3" /> Local demo provider</p><SheetTitle className="flex items-center gap-2"><Bot className="h-5 w-5 text-cyan-400" /> Investigation Assistant</SheetTitle></SheetHeader>
        <div className="assistant-messages flex-1 space-y-4 overflow-y-auto py-5">{messages.map((message, index) => <div key={`${message.role}-${index}`} className={message.role === 'user' ? 'assistant-user-message' : 'assistant-message'}><p className="text-sm leading-6">{message.text}</p>{message.citations.length > 0 && <div className="mt-3 flex flex-wrap gap-1">{message.citations.map((citation) => <Badge key={citation} variant="outline" className="text-[10px]">{citation}</Badge>)}</div>}</div>)}</div>
        <div className="space-y-3 border-t border-border pt-4"><div className="flex flex-wrap gap-2">{Object.keys(mockAssistantResponses).filter((key) => key !== 'default').map((key) => <Button key={key} variant="outline" size="sm" onClick={() => send(key)}>{key}</Button>)}</div><div className="flex gap-2"><Input value={prompt} onChange={(event) => setPrompt(event.target.value)} onKeyDown={(event) => event.key === 'Enter' && send()} placeholder="Ask about this investigation..." /><Button size="icon" onClick={() => send()} disabled={!prompt.trim()} aria-label="Send prompt"><Send className="h-4 w-4" /></Button></div><p className="text-[10px] text-muted-foreground">Responses are local demo content and are not connected to an AI service.</p></div>
      </SheetContent>
    </Sheet>
  )
}

export function NotesPanel() {
  const [notes, setNotes] = useState(['Review the financial relationship before the next case briefing.'])
  const [draft, setDraft] = useState('')
  const addNote = () => { if (draft.trim()) { setNotes((current) => [...current, draft.trim()]); setDraft('') } }
  return <Card><CardHeader className="pb-3"><CardTitle className="flex items-center gap-2 text-sm"><StickyNote className="h-4 w-4 text-amber-400" /> Investigator notes</CardTitle></CardHeader><CardContent className="space-y-3"><div className="flex gap-2"><Input value={draft} onChange={(event) => setDraft(event.target.value)} placeholder="Add a working note..." onKeyDown={(event) => event.key === 'Enter' && addNote()} /><Button size="sm" onClick={addNote}>Add</Button></div>{notes.map((note, index) => <div key={`${note}-${index}`} className="note-row"><span className="h-2 w-2 rounded-full bg-amber-400" /><p>{note}</p><button type="button" onClick={() => setNotes((current) => current.filter((_, noteIndex) => noteIndex !== index))} aria-label="Delete note"><X className="h-3 w-3" /></button></div>)}</CardContent></Card>
}

export function WhyThisObject({ entity }: { entity: Entity }) {
  return <Card className="border-cyan-500/20"><CardHeader className="pb-3"><CardTitle className="flex items-center gap-2 text-sm"><Info className="h-4 w-4 text-cyan-400" /> Why am I seeing this?</CardTitle></CardHeader><CardContent className="space-y-2 text-xs text-muted-foreground"><p><Check className="mr-2 inline h-3 w-3 text-emerald-400" />Connected to {entity.name === 'Raj Kumar' ? 'Northstar Logistics' : 'the active investigation'}</p><p><Check className="mr-2 inline h-3 w-3 text-emerald-400" />Appears in {entity.caseIds.length} demo case{entity.caseIds.length === 1 ? '' : 's'}</p><p><Check className="mr-2 inline h-3 w-3 text-emerald-400" />Referenced by {mockRelationships.filter((relationship) => relationship.sourceEntityId === entity.id || relationship.targetEntityId === entity.id).length} relationship records</p></CardContent></Card>
}

export function EntityReviewCard({ existing, candidate, confidence, signals, onDecision }: { existing: string; candidate: string; confidence: number; signals: string[]; onDecision: (decision: string) => void }) {
  return <Card><CardHeader><div className="flex items-start justify-between"><div><p className="eyebrow">Potential match</p><CardTitle className="text-base">{existing} <span className="text-muted-foreground">↔</span> {candidate}</CardTitle></div><Badge variant="secondary">{Math.round(confidence * 100)}%</Badge></div></CardHeader><CardContent><div className="review-progress"><span style={{ width: `${confidence * 100}%` }} /></div><div className="mt-4 flex flex-wrap gap-2">{signals.map((signal) => <Badge key={signal} variant="outline">{signal}</Badge>)}</div><div className="mt-5 flex gap-2"><Button size="sm" onClick={() => onDecision('approved')}>Accept match</Button><Button size="sm" variant="outline" onClick={() => onDecision('rejected')}>Reject</Button><Button size="sm" variant="ghost" onClick={() => onDecision('later')}>Review later</Button></div></CardContent></Card>
}

export function CrossCasePanel() {
  const [caseA, setCaseA] = useState('CASE-2026-001')
  const [caseB, setCaseB] = useState('CASE-2026-002')
  const shared = mockEntities.filter((entity) => entity.caseIds.includes(caseA) && entity.caseIds.includes(caseB))
  return <Card><CardHeader><CardTitle className="text-base">Cross-case intelligence</CardTitle><p className="text-xs text-muted-foreground">Compare shared objects in the demo dataset.</p></CardHeader><CardContent><div className="grid grid-cols-[1fr_auto_1fr] items-center gap-3"><select className="input h-9" value={caseA} onChange={(event) => setCaseA(event.target.value)}><option>CASE-2026-001</option><option>CASE-2026-002</option><option>CASE-2026-003</option></select><span className="text-xs text-muted-foreground">vs</span><select className="input h-9" value={caseB} onChange={(event) => setCaseB(event.target.value)}><option>CASE-2026-002</option><option>CASE-2026-001</option><option>CASE-2026-003</option></select></div><div className="mt-5 space-y-2">{shared.length > 0 ? shared.map((entity) => <div key={entity.id} className="flex items-center justify-between rounded-lg border border-border p-3 text-sm"><span>{entity.name}</span><Badge variant="outline">{entity.type}</Badge></div>) : <div className="empty-state"><AlertCircle className="h-5 w-5" />No shared entities in this selection.</div>}</div></CardContent></Card>
}
