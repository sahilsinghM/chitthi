'use client'

import { useState } from 'react'
import { api } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { ModelSelector } from './ModelSelector'

interface ComparisonResult {
  model: string
  content: string
  tokens: {
    input: number
    output: number
  }
  estimated_cost: number
  provider: string
  error?: string
  status?: string
}

export function ModelComparison() {
  const [selectedModels, setSelectedModels] = useState<string[]>([])
  const [prompt, setPrompt] = useState('')
  const [comparing, setComparing] = useState(false)
  const [results, setResults] = useState<ComparisonResult[]>([])
  const [error, setError] = useState<string | null>(null)

  const handleAddModel = (modelId: string) => {
    if (!selectedModels.includes(modelId) && selectedModels.length < 5) {
      setSelectedModels([...selectedModels, modelId])
    }
  }

  const handleRemoveModel = (modelId: string) => {
    setSelectedModels(selectedModels.filter(id => id !== modelId))
  }

  const handleCompare = async () => {
    if (selectedModels.length < 2) {
      setError('Please select at least 2 models')
      return
    }
    if (!prompt.trim()) {
      setError('Please enter a prompt')
      return
    }

    try {
      setComparing(true)
      setError(null)
      const result = await api.drafts.compare(selectedModels, prompt)
      setResults(result.comparison || [])
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to compare models')
    } finally {
      setComparing(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Compare Models</CardTitle>
        <CardDescription>Generate drafts with multiple models side-by-side</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label>Select Models (2-5)</Label>
          <div className="flex flex-wrap gap-2">
            {selectedModels.map((modelId) => (
              <div
                key={modelId}
                className="flex items-center gap-2 bg-primary/10 px-3 py-1 rounded-full text-sm"
              >
                <span>{modelId}</span>
                <button
                  onClick={() => handleRemoveModel(modelId)}
                  className="text-destructive hover:text-destructive/80"
                >
                  ×
                </button>
              </div>
            ))}
            {selectedModels.length < 5 && (
              <ModelSelector
                onModelChange={handleAddModel}
                excludeModels={selectedModels}
                placeholder="Add model..."
              />
            )}
          </div>
          {selectedModels.length < 2 && (
            <p className="text-xs text-muted-foreground">
              Select at least 2 models to compare
            </p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="compare-prompt">Prompt</Label>
          <Textarea
            id="compare-prompt"
            placeholder="Enter the prompt to compare models..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={4}
          />
        </div>

        <Button
          onClick={handleCompare}
          disabled={comparing || selectedModels.length < 2 || !prompt.trim()}
          className="w-full"
        >
          {comparing ? 'Comparing...' : 'Compare Models'}
        </Button>

        {error && (
          <div className="text-sm text-destructive bg-destructive/10 p-3 rounded">
            {error}
          </div>
        )}

        {results.length > 0 && (
          <div className="space-y-4 mt-4">
            <h3 className="font-semibold">Comparison Results</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {results.map((result, index) => (
                <Card key={index} className={result.error ? 'border-destructive' : ''}>
                  <CardHeader>
                    <CardTitle className="text-lg">{result.model}</CardTitle>
                    <CardDescription>
                      {result.provider}
                      {result.error && ' • Failed'}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {result.error ? (
                      <p className="text-sm text-destructive">{result.error}</p>
                    ) : (
                      <>
                        <div className="mb-3">
                          <pre className="whitespace-pre-wrap text-sm bg-muted p-3 rounded">
                            {result.content}
                          </pre>
                        </div>
                        <div className="text-xs text-muted-foreground space-y-1">
                          <p>Tokens: {result.tokens.input + result.tokens.output} (in: {result.tokens.input}, out: {result.tokens.output})</p>
                          <p>Cost: ${result.estimated_cost.toFixed(6)}</p>
                        </div>
                      </>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

