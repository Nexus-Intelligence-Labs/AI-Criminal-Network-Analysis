import { useState } from 'react'
import { Copy, Play, Plus, Star, Trash2 } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'

const initialQueries = [
  { id: 'Q-001', name: 'Organization X Network', description: 'All entities connected to Northstar Logistics', type: 'Network' },
  { id: 'Q-002', name: 'High Centrality Entities', description: 'Entities with the highest relationship count', type: 'Analytics' },
  { id: 'Q-003', name: 'Entities Across Cases', description: 'Shared entities between active cases', type: 'Cross-case' },
]

export function SavedQueries() {
  const [queries, setQueries] = useState(initialQueries)
  const [name, setName] = useState('')
  const addQuery = () => { if (name.trim()) { setQueries((current) => [...current, { id: `Q-${current.length + 1}`, name: name.trim(), description: 'New local demo query', type: 'Custom' }]); setName('') } }
  return <div className="page-frame flex-1 overflow-y-auto p-6"><div className="mb-6"><p className="eyebrow">Reusable investigations / Local demo state</p><h1 className="page-title">Saved queries</h1><p className="mt-2 text-sm text-muted-foreground">Keep frequently used investigative searches close at hand.</p></div><Card className="mb-5 max-w-3xl"><CardContent className="flex gap-2 p-4"><Input value={name} onChange={(event) => setName(event.target.value)} placeholder="Name a new query..." /><Button onClick={addQuery}><Plus className="h-4 w-4" /> Save query</Button></CardContent></Card><div className="grid max-w-3xl gap-3">{queries.map((query) => <Card key={query.id}><CardContent className="flex items-center gap-4 p-4"><Star className="h-4 w-4 text-amber-400" /><div className="min-w-0 flex-1"><div className="flex items-center gap-2"><strong>{query.name}</strong><Badge variant="outline">{query.type}</Badge></div><p className="mt-1 text-xs text-muted-foreground">{query.description}</p></div><div className="flex gap-1"><Button size="icon" variant="ghost" aria-label="Run query"><Play className="h-4 w-4" /></Button><Button size="icon" variant="ghost" aria-label="Duplicate query"><Copy className="h-4 w-4" /></Button><Button size="icon" variant="ghost" aria-label="Delete query" onClick={() => setQueries((current) => current.filter((item) => item.id !== query.id))}><Trash2 className="h-4 w-4" /></Button></div></CardContent></Card>)}</div></div>
}
