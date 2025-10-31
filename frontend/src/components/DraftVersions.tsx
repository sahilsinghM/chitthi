'use client'

import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

interface Version {
  id: string
  version_number: number
  content: string
  changes_summary?: string
  created_at: string
}

interface DraftVersionsProps {
  draftId: string
  onSelectVersion?: (version: Version) => void
}

export function DraftVersions({ draftId, onSelectVersion }: DraftVersionsProps) {
  const [versions, setVersions] = useState<Version[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedVersion, setSelectedVersion] = useState<Version | null>(null)

  useEffect(() => {
    loadVersions()
  }, [draftId])

  const loadVersions = async () => {
    try {
      setLoading(true)
      setError(null)
      const result = await api.drafts.getVersions(draftId)
      setVersions(result.versions || [])
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load versions')
    } finally {
      setLoading(false)
    }
  }

  const handleSelectVersion = (version: Version) => {
    setSelectedVersion(version)
    onSelectVersion?.(version)
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Version History</CardTitle>
          <CardDescription>Loading...</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Version History</CardTitle>
          <CardDescription className="text-destructive">{error}</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Version History</CardTitle>
        <CardDescription>{versions.length} version{versions.length !== 1 ? 's' : ''}</CardDescription>
      </CardHeader>
      <CardContent>
        {versions.length === 0 ? (
          <p className="text-muted-foreground text-sm">No versions found</p>
        ) : (
          <div className="space-y-2">
            {versions.map((version) => (
              <div
                key={version.id}
                className={`border rounded-lg p-3 cursor-pointer transition-colors ${
                  selectedVersion?.id === version.id
                    ? 'bg-primary/10 border-primary'
                    : 'hover:bg-muted/50'
                }`}
                onClick={() => handleSelectVersion(version)}
              >
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h4 className="font-semibold">Version {version.version_number}</h4>
                    <p className="text-xs text-muted-foreground">
                      {new Date(version.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                {version.changes_summary && (
                  <p className="text-sm text-muted-foreground mb-2">
                    {version.changes_summary}
                  </p>
                )}
                <p className="text-xs text-muted-foreground line-clamp-2">
                  {version.content.substring(0, 100)}...
                </p>
              </div>
            ))}
          </div>
        )}
        <Button
          onClick={loadVersions}
          variant="outline"
          className="w-full mt-4"
        >
          Refresh
        </Button>
      </CardContent>
    </Card>
  )
}

