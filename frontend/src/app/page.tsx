'use client'

import { useState } from 'react'
import Link from 'next/link'
import { ModelSelector } from '@/components/ModelSelector'
import { DraftGenerator } from '@/components/DraftGenerator'
import { ModelComparison } from '@/components/ModelComparison'
import { DraftList } from '@/components/DraftList'
import { Button } from '@/components/ui/button'

export default function Home() {
  const [selectedModel, setSelectedModel] = useState<string>('')
  const [selectedDraftId, setSelectedDraftId] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'generate' | 'drafts' | 'compare'>('generate')

  return (
    <main className="container mx-auto py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold mb-2">Newsletter Engine</h1>
            <p className="text-muted-foreground">
              AI-powered Hinglish Newsletter Generator
            </p>
          </div>
          <Link href="/analytics">
            <Button variant="outline">Analytics</Button>
          </Link>
        </div>

        <div className="flex gap-2 mb-6 border-b">
          <button
            onClick={() => setActiveTab('generate')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors ${
              activeTab === 'generate'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            Generate Draft
          </button>
          <button
            onClick={() => setActiveTab('drafts')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors ${
              activeTab === 'drafts'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            Saved Drafts
          </button>
          <button
            onClick={() => setActiveTab('compare')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors ${
              activeTab === 'compare'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            Compare Models
          </button>
        </div>
        
        <div className="space-y-8">
          {activeTab === 'generate' && (
            <>
              <ModelSelector onModelChange={setSelectedModel} />
              <DraftGenerator selectedModel={selectedModel} />
            </>
          )}
          {activeTab === 'drafts' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-1">
                <DraftList onSelectDraft={setSelectedDraftId} />
              </div>
              <div className="lg:col-span-2">
                {selectedDraftId ? (
                  <div className="space-y-4">
                    {/* DraftEditor would go here - can be added later */}
                    <div className="border rounded-lg p-4 bg-muted">
                      <p className="text-sm text-muted-foreground">
                        Draft editor coming soon. Use the API directly: GET /api/drafts/{selectedDraftId}
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="border rounded-lg p-8 text-center text-muted-foreground">
                    Select a draft to view details
                  </div>
                )}
              </div>
            </div>
          )}
          {activeTab === 'compare' && (
            <ModelComparison />
          )}
        </div>
      </div>
    </main>
  )
}

