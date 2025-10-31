'use client'

import { useState } from 'react'
import { api } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'

interface DraftGeneratorProps {
  selectedModel: string
}

export function DraftGenerator({ selectedModel }: DraftGeneratorProps) {
  const [context, setContext] = useState('')
  const [generating, setGenerating] = useState(false)
  const [draft, setDraft] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const handleGenerate = async () => {
    if (!selectedModel) {
      setError('Please select a model first')
      return
    }

    try {
      setGenerating(true)
      setError(null)
      const result = await api.drafts.generate(selectedModel, context)
      setDraft(result)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate draft')
    } finally {
      setGenerating(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Generate Draft</CardTitle>
        <CardDescription>Create a Hinglish newsletter draft</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="context">Context / Topic</Label>
          <Textarea
            id="context"
            placeholder="Enter the topic or context for the newsletter..."
            value={context}
            onChange={(e) => setContext(e.target.value)}
            rows={4}
          />
        </div>

        <Button 
          onClick={handleGenerate} 
          disabled={generating || !selectedModel}
          className="w-full"
        >
          {generating ? 'Generating...' : 'Generate Draft'}
        </Button>

        {error && (
          <div className="text-sm text-destructive bg-destructive/10 p-3 rounded">
            {error}
          </div>
        )}

        {draft && (
          <div className="space-y-4 mt-4">
            <div className="border rounded-lg p-4 bg-muted">
              <pre className="whitespace-pre-wrap text-sm">
                {draft.draft.content}
              </pre>
            </div>
            <div className="text-xs text-muted-foreground space-y-1">
              <p>Model: {draft.draft.model} ({draft.draft.provider})</p>
              <p>Tokens: {draft.metadata.tokens.total} (in: {draft.metadata.tokens.input}, out: {draft.metadata.tokens.output})</p>
              <p>Estimated Cost: ${draft.metadata.estimated_cost.toFixed(6)}</p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

