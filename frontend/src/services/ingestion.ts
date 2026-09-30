export interface IngestionRequest {
  filename: string
  content: string
  case_id: string
  source_type: string
}

export interface IngestionPreview {
  filename: string
  case_id: string
  source_type: string
  columns: string[]
  rows: Record<string, unknown>[]
  issues: { row?: number; field?: string; message: string }[]
  provenance: Record<string, unknown>
}

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

async function request<T>(path: string, init: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(getApiAccessToken() ? { Authorization: `Bearer ${getApiAccessToken()}` } : {}),
      ...(init.headers ?? {}),
    },
  })
  if (!response.ok) {
    const body = await response.json().catch(() => null)
    throw new Error(body?.detail ?? `Request failed with status ${response.status}`)
  }
  return response.json() as Promise<T>
}

export const ingestionService = {
  preview(payload: IngestionRequest) {
    return request<IngestionPreview>('/api/ingestion/preview', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  import(payload: IngestionRequest) {
    return request<{ job_id: string; status: string; row_count: number; provenance_path: string; entities_written: number; relationships_written: number }>('/api/ingestion/import', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
}
import { getApiAccessToken } from './auth/apiAuthService'
