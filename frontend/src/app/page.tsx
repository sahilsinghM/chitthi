'use client'

import { useState } from 'react'
import { ModelSelector } from '@/components/ModelSelector'
import { DraftGenerator } from '@/components/DraftGenerator'

export default function Home() {
  const [selectedModel, setSelectedModel] = useState<string>('')

  return (
    <main className="container mx-auto py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-2">Newsletter Engine</h1>
        <p className="text-muted-foreground mb-8">
          AI-powered Hinglish Newsletter Generator
        </p>
        
        <div className="space-y-8">
          <ModelSelector onModelChange={setSelectedModel} />
          <DraftGenerator selectedModel={selectedModel} />
        </div>
      </div>
    </main>
  )
}

