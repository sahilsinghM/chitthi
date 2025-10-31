'use client'

import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

interface Draft {
  id: string
  title?: string
  content: string
  status: string
  model_used?: string
  created_at: string
  updated_at: string
}

interface DraftListProps {
  onSelectDraft?: (draftId: string) => void
  statusFilter?: string
}

export function DraftList({ onSelectDraft, statusFilter }: DraftListProps) {
  const [drafts, setDrafts] = useState<Draft[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadDrafts()
  }, [statusFilter])

  const loadDrafts = async () => {
    try {
      setLoading(true)
      setError(null)
      const result = await api.drafts.list(statusFilter)
      setDrafts(result.drafts || [])
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load drafts')
    } finally {
      setLoading(false)
    }
  }

  const truncateContent = (content: string, maxLength: number = 150) => {
    if (content.length <= maxLength) return content
    return content.substring(0, maxLength) + '...'
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Drafts</CardTitle>
          <CardDescription>Loading drafts...</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Drafts</CardTitle>
          <CardDescription className="text-destructive">{error}</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Drafts</CardTitle>
        <CardDescription>
          {drafts.length} {statusFilter ? statusFilter : ''} draft{drafts.length !== 1 ? 's' : ''}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {drafts.length === 0 ? (
          <p className="text-muted-foreground text-sm">No drafts found</p>
        ) : (
          <div className="space-y-4">
            {drafts.map((draft) => (
              <div
                key={draft.id}
                className="border rounded-lg p-4 hover:bg-muted/50 cursor-pointer transition-colors"
                onClick={() => onSelectDraft?.(draft.id)}
              >
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h3 className="font-semibold">
                      {draft.title || `Draft ${draft.id.substring(0, 8)}`}
                    </h3>
                    <p className="text-xs text-muted-foreground">
                      {new Date(draft.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded ${
                    draft.status === 'published' ? 'bg-green-100 text-green-800' :
                    draft.status === 'final' ? 'bg-blue-100 text-blue-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {draft.status}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground mb-2">
                  {truncateContent(draft.content)}
                </p>
                {draft.model_used && (
                  <p className="text-xs text-muted-foreground">
                    Model: {draft.model_used}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
        <Button
          onClick={loadDrafts}
          variant="outline"
          className="w-full mt-4"
        >
          Refresh
        </Button>
      </CardContent>
    </Card>
  )
}

