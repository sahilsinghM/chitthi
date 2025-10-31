'use client'

import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'

interface Draft {
  id: string
  title?: string
  content: string
  status: string
  model_used?: string
  created_at: string
  updated_at: string
  version?: number
}

interface DraftEditorProps {
  draftId: string
  onClose?: () => void
}

export function DraftEditor({ draftId, onClose }: DraftEditorProps) {
  const [draft, setDraft] = useState<Draft | null>(null)
  const [editedContent, setEditedContent] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [saveSuccess, setSaveSuccess] = useState(false)

  useEffect(() => {
    loadDraft()
  }, [draftId])

  const loadDraft = async () => {
    try {
      setLoading(true)
      setError(null)
      const result = await api.drafts.get(draftId)
      setDraft(result.draft)
      setEditedContent(result.draft.content)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load draft')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    if (!draft || !editedContent) return

    try {
      setSaving(true)
      setError(null)
      setSaveSuccess(false)

      await api.drafts.createVersion(draftId, editedContent, 'Manual edit')
      
      setSaveSuccess(true)
      setTimeout(() => setSaveSuccess(false), 3000)
      
      // Reload to get updated version
      await loadDraft()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save draft')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Loading Draft...</CardTitle>
        </CardHeader>
      </Card>
    )
  }

  if (error && !draft) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Error</CardTitle>
          <CardDescription className="text-destructive">{error}</CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={onClose} variant="outline">Close</Button>
        </CardContent>
      </Card>
    )
  }

  if (!draft) {
    return null
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle>{draft.title || `Draft ${draft.id.substring(0, 8)}`}</CardTitle>
            <CardDescription>
              Created: {new Date(draft.created_at).toLocaleString()}
              {draft.version && ` • Version ${draft.version}`}
            </CardDescription>
          </div>
          <div className="flex gap-2">
            <Button onClick={handleSave} disabled={saving || editedContent === draft.content}>
              {saving ? 'Saving...' : 'Save Version'}
            </Button>
            {onClose && (
              <Button onClick={onClose} variant="outline">Close</Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {error && (
          <div className="text-sm text-destructive bg-destructive/10 p-3 rounded">
            {error}
          </div>
        )}
        {saveSuccess && (
          <div className="text-sm text-green-600 bg-green-50 p-3 rounded">
            Draft saved successfully!
          </div>
        )}
        
        <div className="space-y-2">
          <Label htmlFor="content">Content</Label>
          <Textarea
            id="content"
            value={editedContent}
            onChange={(e) => setEditedContent(e.target.value)}
            rows={20}
            className="font-mono text-sm"
          />
        </div>

        <div className="flex gap-4 text-sm text-muted-foreground">
          {draft.model_used && (
            <span>Model: {draft.model_used}</span>
          )}
          <span>Status: {draft.status}</span>
          <span>Updated: {new Date(draft.updated_at).toLocaleString()}</span>
        </div>
      </CardContent>
    </Card>
  )
}

