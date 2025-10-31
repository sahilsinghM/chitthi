'use client'

import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

interface UsageStats {
  total_requests: number
  total_input_tokens: number
  total_output_tokens: number
  total_tokens: number
  total_cost: number
  by_provider: Record<string, {
    cost: number
    requests: number
    tokens: number
  }>
  by_operation: Record<string, {
    cost: number
    requests: number
  }>
  period_days: number
}

interface CostBreakdown {
  total_cost: number
  by_provider: Record<string, {
    total: number
    count: number
    avg_per_request: number
  }>
  by_model: Record<string, {
    total: number
    count: number
  }>
  period: string
  total_requests: number
}

export function CostDashboard() {
  const [usageStats, setUsageStats] = useState<UsageStats | null>(null)
  const [costBreakdown, setCostBreakdown] = useState<CostBreakdown | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [days, setDays] = useState(30)

  useEffect(() => {
    loadData()
  }, [days])

  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)
      const [usage, costs] = await Promise.all([
        api.analytics.usage(undefined, days),
        api.analytics.costs()
      ])
      setUsageStats(usage)
      setCostBreakdown(costs)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load analytics')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Cost Dashboard</CardTitle>
          <CardDescription>Loading...</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Cost Dashboard</CardTitle>
          <CardDescription className="text-destructive">{error}</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Cost Dashboard</CardTitle>
          <CardDescription>
            Analytics for the last {days} days
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 mb-4">
            <button
              onClick={() => setDays(7)}
              className={`px-3 py-1 rounded text-sm ${days === 7 ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}
            >
              7 days
            </button>
            <button
              onClick={() => setDays(30)}
              className={`px-3 py-1 rounded text-sm ${days === 30 ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}
            >
              30 days
            </button>
            <button
              onClick={() => setDays(90)}
              className={`px-3 py-1 rounded text-sm ${days === 90 ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}
            >
              90 days
            </button>
          </div>
        </CardContent>
      </Card>

      {usageStats && (
        <Card>
          <CardHeader>
            <CardTitle>Usage Statistics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Total Requests</p>
                <p className="text-2xl font-bold">{usageStats.total_requests}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Tokens</p>
                <p className="text-2xl font-bold">{usageStats.total_tokens.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Cost</p>
                <p className="text-2xl font-bold">${usageStats.total_cost.toFixed(4)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Avg per Request</p>
                <p className="text-2xl font-bold">
                  ${usageStats.total_requests > 0 ? (usageStats.total_cost / usageStats.total_requests).toFixed(6) : '0.000000'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {costBreakdown && (
        <>
          <Card>
            <CardHeader>
              <CardTitle>Cost by Provider</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(costBreakdown.by_provider).map(([provider, data]) => (
                  <div key={provider} className="flex justify-between items-center p-3 bg-muted rounded">
                    <div>
                      <p className="font-semibold capitalize">{provider}</p>
                      <p className="text-sm text-muted-foreground">
                        {data.count} request{data.count !== 1 ? 's' : ''}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold">${data.total.toFixed(4)}</p>
                      <p className="text-xs text-muted-foreground">
                        ${data.avg_per_request.toFixed(6)} avg
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Cost by Operation</CardTitle>
            </CardHeader>
            <CardContent>
              {usageStats?.by_operation && (
                <div className="space-y-3">
                  {Object.entries(usageStats.by_operation).map(([operation, data]) => (
                    <div key={operation} className="flex justify-between items-center p-3 bg-muted rounded">
                      <div>
                        <p className="font-semibold capitalize">{operation}</p>
                        <p className="text-sm text-muted-foreground">
                          {data.requests} request{data.requests !== 1 ? 's' : ''}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-bold">${data.cost.toFixed(4)}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Cost by Model</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(costBreakdown.by_model).map(([model, data]) => (
                  <div key={model} className="flex justify-between items-center p-3 bg-muted rounded">
                    <div>
                      <p className="font-semibold">{model}</p>
                      <p className="text-sm text-muted-foreground">
                        {data.count} request{data.count !== 1 ? 's' : ''}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold">${data.total.toFixed(4)}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}

