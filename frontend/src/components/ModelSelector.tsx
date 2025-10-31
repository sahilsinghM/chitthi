'use client'

import { useState, useEffect } from 'react'
import { api, ModelInfo } from '@/lib/api'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

interface ModelSelectorProps {
  onModelChange: (modelId: string) => void
  excludeModels?: string[]
  placeholder?: string
}

export function ModelSelector({ onModelChange, excludeModels = [], placeholder = "Select a model" }: ModelSelectorProps) {
  const [models, setModels] = useState<ModelInfo[]>([])
  const [selectedModel, setSelectedModel] = useState<string>('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadModels()
  }, [])  // eslint-disable-line react-hooks/exhaustive-deps

  const loadModels = async () => {
    try {
      setLoading(true)
      const modelList = await api.models.list()
      setModels(modelList)
      if (modelList.length > 0 && !selectedModel) {
        const firstModel = modelList[0].id
        setSelectedModel(firstModel)
        onModelChange(firstModel)
      }
    } catch (error) {
      console.error('Failed to load models:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleModelChange = (modelId: string) => {
    setSelectedModel(modelId)
    onModelChange(modelId)
  }

  const selectedModelInfo = models.find(m => m.id === selectedModel)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Select Model</CardTitle>
        <CardDescription>Choose an AI model for draft generation</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Select value={selectedModel} onValueChange={handleModelChange}>
          <SelectTrigger>
            <SelectValue placeholder={placeholder} />
          </SelectTrigger>
          <SelectContent>
            {models.filter(model => !excludeModels.includes(model.id)).map((model) => (
              <SelectItem key={model.id} value={model.id}>
                <div className="flex items-center justify-between w-full">
                  <span>{model.display_name}</span>
                  <span className="text-xs text-muted-foreground ml-2">
                    {model.provider}
                  </span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {selectedModelInfo && (
          <div className="text-sm space-y-1">
            <p className="text-muted-foreground">
              {selectedModelInfo.description}
            </p>
            <div className="flex gap-4 text-xs">
              <span>
                Input: ${selectedModelInfo.cost_per_1k_input.toFixed(4)}/1k tokens
              </span>
              <span>
                Output: ${selectedModelInfo.cost_per_1k_output.toFixed(4)}/1k tokens
              </span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

