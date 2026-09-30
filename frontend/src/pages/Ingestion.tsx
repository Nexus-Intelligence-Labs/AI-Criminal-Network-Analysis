import { useState } from 'react'
import { Link } from 'react-router-dom'
import { AlertTriangle, Database, Upload } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { ingestionService, type IngestionPreview, type IngestionRequest } from '@/services/ingestion'

export function Ingestion() {
  const [request, setRequest] = useState<IngestionRequest>({
    filename: '',
    content: '',
    case_id: '',
    source_type: 'structured-records',
  })
  const [preview, setPreview] = useState<IngestionPreview | null>(null)
  const [message, setMessage] = useState('')
  const [importResult, setImportResult] = useState<{ job_id: string; row_count: number; entities_written: number; relationships_written: number } | null>(null)
  const [busy, setBusy] = useState(false)

  async function readFile(file: File) {
    const content = await file.text()
    setRequest((current) => ({ ...current, filename: file.name, content }))
    setPreview(null)
    setMessage('')
  }

  async function validate() {
    setBusy(true)
    setMessage('')
    try {
      setPreview(await ingestionService.preview(request))
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Preview failed.')
    } finally {
      setBusy(false)
    }
  }

  async function importSource() {
    setBusy(true)
    setMessage('')
    try {
      const result = await ingestionService.import(request)
      setImportResult(result)
      setMessage(`Import ${result.status}. Job ${result.job_id} completed.`)
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Import failed.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page-frame flex-1 overflow-y-auto p-6">
      <div className="page-header mb-6">
        <p className="eyebrow">Data operations / authenticated</p>
        <h1 className="page-title">Source ingestion</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Upload a source record, inspect validation results, and preserve provenance before import.
        </p>
      </div>
      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2"><Upload className="h-5 w-5" /> Source and case</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <Input type="file" accept=".csv,.json,.txt" onChange={(event) => {
              const file = event.target.files?.[0]
              if (file) void readFile(file)
            }} />
            <Input placeholder="Case ID" value={request.case_id} onChange={(event) => setRequest({ ...request, case_id: event.target.value })} />
            <Input placeholder="Source type" value={request.source_type} onChange={(event) => setRequest({ ...request, source_type: event.target.value })} />
            <div className="rounded-md border bg-muted/30 p-3 text-xs text-muted-foreground">
              {request.filename ? `${request.filename} · ${request.content.length} characters loaded` : 'Choose a CSV, JSON, or TXT source file.'}
            </div>
            <div className="flex gap-2">
              <Button disabled={busy || !request.content || !request.case_id} onClick={() => void validate()}>Validate and preview</Button>
              <Button variant="outline" disabled={busy || !preview || Boolean(preview.issues.length)} onClick={() => void importSource()}>Import validated source</Button>
            </div>
            {message && <p className="text-sm text-muted-foreground">{message}</p>}
            {importResult && <div className="rounded-md border border-primary/30 bg-primary/5 p-3 text-sm">
              <p>Records imported: {importResult.row_count}</p>
              <p>Entities created/updated: {importResult.entities_written}</p>
              <p>Relationships created/updated: {importResult.relationships_written}</p>
              <Button asChild className="mt-3" variant="outline"><Link to={`/graph?case=${encodeURIComponent(request.case_id)}`}>Open graph</Link></Button>
            </div>}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2"><Database className="h-5 w-5" /> Validation and provenance</CardTitle></CardHeader>
          <CardContent>
            {!preview ? <p className="text-sm text-muted-foreground">Preview results will appear here before any import is accepted.</p> : (
              <div className="space-y-4">
                <div className="flex flex-wrap gap-2"><Badge variant="outline">{preview.rows.length} preview rows</Badge><Badge variant={preview.issues.length ? 'destructive' : 'default'}>{preview.issues.length ? `${preview.issues.length} issues` : 'validated'}</Badge></div>
                {preview.issues.length > 0 && <div className="space-y-2 text-sm text-destructive">{preview.issues.map((issue, index) => <p key={`${issue.message}-${index}`} className="flex gap-2"><AlertTriangle className="h-4 w-4 shrink-0" />{issue.row ? `Row ${issue.row}: ` : ''}{issue.message}</p>)}</div>}
                <div className="rounded-md border p-3 text-xs text-muted-foreground"><p>Source: {String(preview.provenance.source_filename)}</p><p>Case: {preview.case_id}</p><p>Records: {String(preview.provenance.record_count)}</p></div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
